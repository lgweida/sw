package com.example.client.service;

import com.example.client.model.AmendRequest;
import com.example.client.model.CancelRequest;
import com.example.client.model.OrderRequest;
import com.example.client.model.OrderResponse;
import com.example.client.model.SessionStatus;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.annotation.Lazy;
import org.springframework.stereotype.Service;
import quickfix.*;
import quickfix.SessionSettings;
import quickfix.field.*;
import quickfix.field.OnBehalfOfCompID;
import quickfix.fix42.NewOrderSingle;
import quickfix.fix42.OrderCancelReplaceRequest;
import quickfix.fix42.OrderCancelRequest;

import java.math.BigDecimal;
import java.time.LocalDateTime;          // <-- ADD THIS IMPORT
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@Slf4j
@Service
public class OrderService {

  private final SocketInitiator initiator;
  private final SessionSettings sessionSettings;

  // Track sent orders
  private final Map<String, OrderResponse> sentOrders = new ConcurrentHashMap<>();

  // Use @Lazy to break circular dependency
  public OrderService(@Lazy SocketInitiator initiator, SessionSettings sessionSettings) {
    this.initiator       = initiator;
    this.sessionSettings = sessionSettings;
  }

  public OrderResponse sendOrder(OrderRequest request) throws SessionNotFound {
    SessionID sessionId = resolveSession(request.getNetwork(), request.getBrokerCode());

    if (sessionId == null) {
      throw new IllegalStateException("No active FIX session available");
    }

    String clOrdId = generateClOrdId();

    // FIX 4.2 NewOrderSingle requires: ClOrdID, HandlInst, Symbol, Side, TransactTime, OrdType
    NewOrderSingle order = new NewOrderSingle();
    //  new quickfix.fix42.NewOrderSingle(
                // new ClOrdID(clOrdId), new HandlInst('1'), new Symbol(request.getSymbol()),
                // sideToFIXSide(request.getSide()), new TransactTime(), typeToFIXType(request.getOrderType()));

    order.set(new ClOrdID(clOrdId));
    // HandlInst mandatory – use literal '1' for "Automated execution order, private"
    order.set(new HandlInst('1'));                       // <-- FIXED
    order.set(new Symbol(request.getSymbol()));
    order.set(new Side(request.getSide().equalsIgnoreCase("BUY") ? Side.BUY : Side.SELL));
    // order.set(new TransactTime(new java.util.Date()));
    TransactTime transactTime = new TransactTime();
    // transactTime.setValue(new Date());                 // FIX 4.2 expects java.util.Date
    order.set(transactTime);
    order.set(new OrdType(request.getOrderType().equalsIgnoreCase("MARKET")
        ? OrdType.MARKET : OrdType.LIMIT));

    // Optional fields
    order.set(new OrderQty(request.getQuantity()));
    order.set(new TimeInForce(TimeInForce.DAY));

    if (request.getOrderType().equalsIgnoreCase("LIMIT")) {
      if (request.getPrice() == null) {
        throw new IllegalArgumentException("Price is required for LIMIT orders");
      }
      order.set(new Price(request.getPrice().doubleValue()));
    }

    Session.sendToTarget(order, sessionId);

    // Bloomberg UUID — sent as a custom string field (tag 9880 is a common convention;
    // adjust the tag number to match your Bloomberg EMSX configuration)
    if ("BLOOMBERG".equalsIgnoreCase(request.getNetwork()) && request.getUuid() != null) {
      order.setString(9880, request.getUuid());
    }

    // OnBehalfOfCompID — FIX tag 115 lives in the header (tag 116 is DeliverToCompID;
    // tag 115 is the standard "OnBehalfOfCompID" header field used by NYFIX/TradeWare/TradeWeb)
    if (request.getOnBehalfOfCompId() != null && !request.getOnBehalfOfCompId().isBlank()) {
      order.getHeader().setString(OnBehalfOfCompID.FIELD, request.getOnBehalfOfCompId());
    }

    OrderResponse response = OrderResponse.builder()
        .clOrdId(clOrdId)
        .symbol(request.getSymbol())
        .side(request.getSide().toUpperCase())
        .orderType(request.getOrderType().toUpperCase())
        .quantity(request.getQuantity())
        .price(request.getPrice())
        .status("PENDING")
        .timestamp(LocalDateTime.now())
        .build();

    sentOrders.put(clOrdId, response);

    log.info("Sent order: {} {} {} {} @ {}",
        clOrdId, request.getSide(), request.getQuantity(),
        request.getSymbol(), request.getPrice());

    return response;
  }

  public OrderResponse cancelOrder(CancelRequest request) throws SessionNotFound {
    SessionID sessionId = getActiveSession();

    if (sessionId == null) {
      throw new IllegalStateException("No active FIX session available");
    }

    String clOrdId = generateClOrdId();

    // FIX 4.2 OrderCancelRequest requires: OrigClOrdID, ClOrdID, Symbol, Side, TransactTime
    OrderCancelRequest cancelRequest = new OrderCancelRequest();

    cancelRequest.set(new OrigClOrdID(request.getOriginalClOrdId()));
    cancelRequest.set(new ClOrdID(clOrdId));
    cancelRequest.set(new Symbol(request.getSymbol()));  // Symbol is mandatory in FIX 4.2
    cancelRequest.set(new Side(request.getSide().equalsIgnoreCase("BUY") ? Side.BUY : Side.SELL));
    // cancelRequest.set(new TransactTime(new Date()));

    // OrderQty is optional for cancel requests; set to 0 (or omit if not needed)
    cancelRequest.set(new OrderQty(0));

    Session.sendToTarget(cancelRequest, sessionId);

    // Mark the ORIGINAL order as pending cancel immediately (UI feedback)
    OrderResponse original = sentOrders.get(request.getOriginalClOrdId());
    if (original != null) {
      original.setStatus("PENDING_CANCEL");
    }

    OrderResponse response = OrderResponse.builder()
        .clOrdId(clOrdId)
        .symbol(request.getSymbol())
        .side(request.getSide().toUpperCase())
        .status("PENDING_CANCEL")
        .timestamp(LocalDateTime.now())
        .build();

    log.info("Sent cancel request: {} for original order {}", clOrdId, request.getOriginalClOrdId());

    return response;
  }

  public OrderResponse amendOrder(AmendRequest request) throws SessionNotFound {
    SessionID sessionId = getActiveSession();

    if (sessionId == null) {
      throw new IllegalStateException("No active FIX session available");
    }

    // Get the original order to get current values
    OrderResponse originalOrder = sentOrders.get(request.getOriginalClOrdId());
    if (originalOrder == null) {
      throw new IllegalArgumentException("Original order not found: " + request.getOriginalClOrdId());
    }

    String clOrdId = generateClOrdId();

    // FIX 4.2 OrderCancelReplaceRequest requires: OrigClOrdID, ClOrdID, HandlInst, Symbol, Side, TransactTime, OrdType
    OrderCancelReplaceRequest amendRequest = new OrderCancelReplaceRequest();

    amendRequest.set(new OrigClOrdID(request.getOriginalClOrdId()));
    amendRequest.set(new ClOrdID(clOrdId));
    amendRequest.set(new HandlInst('1'));                // <-- FIXED
    amendRequest.set(new Symbol(request.getSymbol()));
    amendRequest.set(new Side(request.getSide().equalsIgnoreCase("BUY") ? Side.BUY : Side.SELL));
    // amendRequest.set(new TransactTime(new Date()));
    amendRequest.set(new OrdType(originalOrder.getOrderType().equalsIgnoreCase("MARKET")
        ? OrdType.MARKET : OrdType.LIMIT));

    // Set new quantity or use original
    int effectiveQty = request.getNewQuantity() != null
        ? request.getNewQuantity()
        : originalOrder.getQuantity();
    amendRequest.set(new OrderQty(effectiveQty));

    // Set new price or use original
    BigDecimal effectivePrice = request.getNewPrice() != null
        ? request.getNewPrice()
        : originalOrder.getPrice();
    if (effectivePrice != null) {
      amendRequest.set(new Price(effectivePrice.doubleValue()));
    }

    Session.sendToTarget(amendRequest, sessionId);

    // Create response for the new (amended) order
    OrderResponse response = OrderResponse.builder()
        .clOrdId(clOrdId)
        .symbol(request.getSymbol())
        .side(request.getSide().toUpperCase())
        .orderType(originalOrder.getOrderType())
        .quantity(effectiveQty)
        .price(effectivePrice)
        .status("PENDING_REPLACE")
        .timestamp(LocalDateTime.now())
        .build();

    // Track the new order
    sentOrders.put(clOrdId, response);

    log.info("Sent amend request: {} for original order {} newQty={} newPrice={}",
        clOrdId, request.getOriginalClOrdId(), effectiveQty, effectivePrice);

    return response;
  }

  /**
   * Update order status based on execution report.
   * Called by ClientFixApplication when execution reports are received.
   */
  public void updateOrderStatus(String clOrdId, String status, int filledQty, int leavesQty) {
    OrderResponse order = sentOrders.get(clOrdId);
    if (order != null) {
      order.setStatus(status);
      order.setFilledQuantity(filledQty);
      order.setLeavesQuantity(leavesQty);
      log.debug("Updated order {} status to {}", clOrdId, status);
    }
  }

  /**
   * Handle order replacement - remove old order and update new order status
   */
  public void handleOrderReplaced(String origClOrdId, String newClOrdId, String status,
                                  int filledQty, int leavesQty) {
    // Mark old order as replaced
    OrderResponse oldOrder = sentOrders.get(origClOrdId);
    if (oldOrder != null) {
      oldOrder.setStatus("REPLACED");
    }

    // Update new order
    updateOrderStatus(newClOrdId, status, filledQty, leavesQty);

    log.debug("Order replaced: {} -> {}", origClOrdId, newClOrdId);
  }

  /**
   * Remove an order from tracking (e.g., when fully filled or cancelled)
   */
  public void removeOrder(String clOrdId) {
    sentOrders.remove(clOrdId);
    log.debug("Removed order {} from tracking", clOrdId);
  }

  public List<SessionStatus> getSessionStatus() {
    List<SessionStatus> statuses = new ArrayList<>();

    for (SessionID sessionId : initiator.getSessions()) {
      Session session = Session.lookupSession(sessionId);
      statuses.add(SessionStatus.builder()
          .sessionId(sessionId.toString())
          .loggedOn(session != null && session.isLoggedOn())
          .senderCompId(sessionId.getSenderCompID())
          .targetCompId(sessionId.getTargetCompID())
          .build());
    }

    return statuses;
  }

  public void updateOrderStatusForCancel(String origClOrdId, String status, int filledQty, int leavesQty) {
    OrderResponse order = sentOrders.get(origClOrdId);
    if (order != null) {
      order.setStatus(status);
      order.setFilledQuantity(filledQty);
      order.setLeavesQuantity(leavesQty);
      log.debug("Updated ORIGINAL order {} status to {}", origClOrdId, status);
    } else {
      log.warn("Cancel update: original order {} not found in sentOrders", origClOrdId);
    }
  }

  public List<OrderResponse> getSentOrders() {
    return new ArrayList<>(sentOrders.values());
  }

  /**
   * Get only open orders (not filled, cancelled, or replaced)
   */
  public List<OrderResponse> getOpenOrders() {
    return sentOrders.values().stream()
        .filter(order -> {
          String status = order.getStatus();
          return status != null &&
              !status.equals("FILLED") &&
              !status.equals("CANCELLED") &&
              !status.equals("REJECTED") &&
              !status.equals("REPLACED");
        })
        .collect(Collectors.toList());
  }

  public OrderResponse getOrderByClOrdId(String clOrdId) {
    return sentOrders.get(clOrdId);
  }

  private SessionID getActiveSession() {
    return resolveSession(null, null);
  }

  /**
   * Resolve the correct FIX session using the {@code Network} and {@code BrokerCode}
   * custom properties declared in quickfix-client.cfg.
   *
   * <p>Matching priority:
   * <ol>
   *   <li>Session whose {@code Network} AND {@code BrokerCode} both match exactly → used immediately.</li>
   *   <li>Session whose {@code Network} matches and has no specific broker code requirement → kept as candidate.</li>
   *   <li>First logged-on session → last-resort fallback when no network is specified.</li>
   * </ol>
   */
  private SessionID resolveSession(String network, String brokerCode) {
    String netUpper    = (network    != null && !network.isBlank())    ? network.toUpperCase()    : null;
    String brokerUpper = (brokerCode != null && !brokerCode.isBlank()) ? brokerCode.toUpperCase() : null;

    SessionID networkOnlyMatch = null;  // candidate when network matches but broker is unspecified
    SessionID firstLoggedOn    = null;  // absolute fallback

    for (SessionID sid : initiator.getSessions()) {
      Session session = Session.lookupSession(sid);
      if (session == null || !session.isLoggedOn()) {
        continue;
      }

      // Read the custom properties we added to quickfix-client.cfg
      String cfgNetwork = getSessionProperty(sid, "Network",    "NONE");
      String cfgBroker  = getSessionProperty(sid, "BrokerCode", "NONE");

      // Track the very first logged-on session as a last resort
      if (firstLoggedOn == null) {
        firstLoggedOn = sid;
      }

      if (netUpper == null) {
        // No routing preference — caller will use firstLoggedOn fallback below
        continue;
      }

      if (!cfgNetwork.equalsIgnoreCase(netUpper)) {
        continue; // wrong network — skip
      }

      // Network matches — now check broker code
      if (brokerUpper != null && cfgBroker.equalsIgnoreCase(brokerUpper)) {
        return sid; // exact network + broker match — use immediately
      }

      if (brokerUpper == null && networkOnlyMatch == null) {
        networkOnlyMatch = sid; // network-only match, keep as candidate
      }

      // If broker requested but this session has NONE, keep as weaker candidate
      if (brokerUpper != null && cfgBroker.equalsIgnoreCase("NONE") && networkOnlyMatch == null) {
        networkOnlyMatch = sid;
      }
    }

    if (networkOnlyMatch != null) return networkOnlyMatch;
    return firstLoggedOn; // null if nothing is logged on
  }

  /**
   * Safely read a custom string property from the session's settings block.
   * Returns {@code defaultValue} if the key is absent or settings lookup fails.
   */
  private String getSessionProperty(SessionID sid, String key, String defaultValue) {
    try {
      return sessionSettings.getString(sid, key);
    } catch (Exception e) {
      return defaultValue;
    }
  }

  private String generateClOrdId() {
    return UUID.randomUUID().toString().substring(0, 8).toUpperCase();
  }
}