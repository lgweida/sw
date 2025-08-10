import dash
from dash import html, dcc
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

# 额外的CSS样式
additional_styles = html.Style("""
.alert-bar p{margin:0}.alert-bar-container .alert-bar .close-btn mat-icon{color:#2a394f;position:relative;right:2px}.alert-bar-container .alert-bar mat-icon{margin:0 10px}.alert-bar-container .alert-bar mat-icon.cancel{color:#e16f5a}.alert-bar-container .alert-bar mat-icon.warning{color:#f2a13f}.alert-bar-container .alert-bar mat-icon.info{color:#2c4191}.alert-bar-container .alert-bar mat-icon.check_circle_outline{color:#4db0de}.alert-bar-container .mat-icon.error_outline{color:red}.alert-bar-container .mat-icon.warning{color:#faa838}.alert-bar-container .close-btn{z-index:2;background-color:transparent;border:none;box-sizing:content-box}.alert-bar-container .close-btn mat-icon{color:#2a394f}@media only screen and (max-width: 420px){.alert-bar-container{min-width:20rem;max-width:20rem}}

mat-menu{display:none}.mat-menu-panel{min-width:112px;max-width:280px;overflow:auto;-webkit-overflow-scrolling:touch;max-height:calc(100vh - 48px);border-radius:4px;outline:0;min-height:64px;position:relative}.mat-menu-panel.ng-animating{pointer-events:none}.cdk-high-contrast-active .mat-menu-panel{outline:solid 1px}.mat-menu-content:not(:empty){padding-top:8px;padding-bottom:8px}.mat-menu-item{-webkit-user-select:none;user-select:none;cursor:pointer;outline:none;border:none;-webkit-tap-highlight-color:rgba(0,0,0,0);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block;line-height:48px;height:48px;padding:0 16px;text-align:left;text-decoration:none;max-width:100%;position:relative}.mat-menu-item::-moz-focus-inner{border:0}.mat-menu-item[disabled]{cursor:default}[dir=rtl] .mat-menu-item{text-align:right}.mat-menu-item .mat-icon{margin-right:16px;vertical-align:middle}.mat-menu-item .mat-icon svg{vertical-align:top}[dir=rtl] .mat-menu-item .mat-icon{margin-left:16px;margin-right:0}.mat-menu-item[disabled]::after{display:block;position:absolute;content:"";top:0;left:0;bottom:0;right:0}.cdk-high-contrast-active .mat-menu-item{margin-top:1px}.mat-menu-item-submenu-trigger{padding-right:32px}[dir=rtl] .mat-menu-item-submenu-trigger{padding-right:16px;padding-left:32px}.mat-menu-submenu-icon{position:absolute;top:50%;right:16px;transform:translateY(-50%);width:5px;height:10px;fill:currentColor}[dir=rtl] .mat-menu-submenu-icon{right:auto;left:16px;transform:translateY(-50%) scaleX(-1)}.cdk-high-contrast-active .mat-menu-submenu-icon{fill:CanvasText}button.mat-menu-item{width:100%}.mat-menu-item .mat-menu-ripple{top:0;left:0;right:0;bottom:0;position:absolute;pointer-events:none}

.mat-button .mat-button-focus-overlay,.mat-icon-button .mat-button-focus-overlay{opacity:0}.mat-button:hover:not(.mat-button-disabled) .mat-button-focus-overlay,.mat-stroked-button:hover:not(.mat-button-disabled) .mat-button-focus-overlay{opacity:.04}@media(hover: none){.mat-button:hover:not(.mat-button-disabled) .mat-button-focus-overlay,.mat-stroked-button:hover:not(.mat-button-disabled) .mat-button-focus-overlay{opacity:0}}.mat-button,.mat-icon-button,.mat-stroked-button,.mat-flat-button{box-sizing:border-box;position:relative;-webkit-user-select:none;user-select:none;cursor:pointer;outline:none;border:none;-webkit-tap-highlight-color:rgba(0,0,0,0);display:inline-block;white-space:nowrap;text-decoration:none;vertical-align:baseline;text-align:center;margin:0;min-width:64px;line-height:36px;padding:0 16px;border-radius:4px;overflow:visible}.mat-button::-moz-focus-inner,.mat-icon-button::-moz-focus-inner,.mat-stroked-button::-moz-focus-inner,.mat-flat-button::-moz-focus-inner{border:0}.mat-button.mat-button-disabled,.mat-icon-button.mat-button-disabled,.mat-stroked-button.mat-button-disabled,.mat-flat-button.mat-button-disabled{cursor:default}.mat-button.cdk-keyboard-focused .mat-button-focus-overlay,.mat-button.cdk-program-focused .mat-button-focus-overlay,.mat-icon-button.cdk-keyboard-focused .mat-button-focus-overlay,.mat-icon-button.cdk-program-focused .mat-button-focus-overlay,.mat-stroked-button.cdk-keyboard-focused .mat-button-focus-overlay,.mat-stroked-button.cdk-program-focused .mat-button-focus-overlay,.mat-flat-button.cdk-keyboard-focused .mat-button-focus-overlay,.mat-flat-button.cdk-program-focused .mat-button-focus-overlay{opacity:.12}.mat-button::-moz-focus-inner,.mat-icon-button::-moz-focus-inner,.mat-stroked-button::-moz-focus-inner,.mat-flat-button::-moz-focus-inner{border:0}.mat-raised-button{box-sizing:border-box;position:relative;-webkit-user-select:none;user-select:none;cursor:pointer;outline:none;border:none;-webkit-tap-highlight-color:rgba(0,0,0,0);display:inline-block;white-space:nowrap;text-decoration:none;vertical-align:baseline;text-align:center;margin:0;min-width:64px;line-height:36px;padding:0 16px;border-radius:4px;overflow:visible;transform:translate3d(0, 0, 0);transition:background 400ms cubic-bezier(0.25, 0.8, 0.25, 1),box-shadow 280ms cubic-bezier(0.4, 0, 0.2, 1)}.mat-raised-button::-moz-focus-inner{border:0}.mat-raised-button.mat-button-disabled{cursor:default}.mat-raised-button.cdk-keyboard-focused .mat-button-focus-overlay,.mat-raised-button.cdk-program-focused .mat-button-focus-overlay{opacity:.12}.mat-raised-button::-moz-focus-inner{border:0}.mat-raised-button._mat-animation-noopable{transition:none !important;animation:none !important}.mat-stroked-button{border:1px solid currentColor;padding:0 15px;line-height:34px}.mat-stroked-button .mat-button-ripple.mat-ripple,.mat-stroked-button .mat-button-focus-overlay{top:-1px;left:-1px;right:-1px;bottom:-1px}.mat-fab{box-sizing:border-box;position:relative;-webkit-user-select:none;user-select:none;cursor:pointer;outline:none;border:none;-webkit-tap-highlight-color:rgba(0,0,0,0);display:inline-block;white-space:nowrap;text-decoration:none;vertical-align:baseline;text-align:center;margin:0;min-width:64px;line-height:36px;padding:0 16px;border-radius:4px;overflow:visible;transform:translate3d(0, 0, 0);transition:background 400ms cubic-bezier(0.25, 0.8, 0.25, 1),box-shadow 280ms cubic-bezier(0.4, 0, 0.2, 1);min-width:0;border-radius:50%;width:56px;height:56px;padding:0;flex-shrink:0}.mat-fab::-moz-focus-inner{border:0}.mat-fab.mat-button-disabled{cursor:default}.mat-fab.cdk-keyboard-focused .mat-button-focus-overlay,.mat-fab.cdk-program-focused .mat-button-focus-overlay{opacity:.12}.mat-fab::-moz-focus-inner{border:0}.mat-fab._mat-animation-noopable{transition:none !important;animation:none !important}.mat-fab .mat-button-wrapper{padding:16px 0;display:inline-block;line-height:24px}.mat-mini-fab{box-sizing:border-box;position:relative;-webkit-user-select:none;user-select:none;cursor:pointer;outline:none;border:none;-webkit-tap-highlight-color:rgba(0,0,0,0);display:inline-block;white-space:nowrap;text-decoration:none;vertical-align:baseline;text-align:center;margin:0;min-width:64px;line-height:36px;padding:0 16px;border-radius:4px;overflow:visible;transform:translate3d(0, 0, 0);transition:background 400ms cubic-bezier(0.25, 0.8, 0.25, 1),box-shadow 280ms cubic-bezier(0.4, 0, 0.2, 1);min-width:0;border-radius:50%;width:40px;height:40px;padding:0;flex-shrink:0}.mat-mini-fab::-moz-focus-inner{border:0}.mat-mini-fab.mat-button-disabled{cursor:default}.mat-mini-fab.cdk-keyboard-focused .mat-button-focus-overlay,.mat-mini-fab.cdk-program-focused .mat-button-focus-overlay{opacity:.12}.mat-mini-fab::-moz-focus-inner{border:0}.mat-mini-fab._mat-animation-noopable{transition:none !important;animation:none !important}.mat-mini-fab .mat-button-wrapper{padding:8px 0;display:inline-block;line-height:24px}.mat-icon-button{padding:0;min-width:0;width:40px;height:40px;flex-shrink:0;line-height:40px;border-radius:50%}.mat-icon-button i,.mat-icon-button .mat-icon{line-height:24px}.mat-button-ripple.mat-ripple,.mat-button-focus-overlay{top:0;left:0;right:0;bottom:0;position:absolute;pointer-events:none;border-radius:inherit}.mat-button-ripple.mat-ripple:not(:empty){transform:translateZ(0)}.mat-button-focus-overlay{opacity:0;transition:opacity 200ms cubic-bezier(0.35, 0, 0.25, 1),background-color 200ms cubic-bezier(0.35, 0, 0.25, 1)}._mat-animation-noopable .mat-button-focus-overlay{transition:none}.mat-button-ripple-round{border-radius:50%;z-index:1}.mat-button .mat-button-wrapper>*,.mat-flat-button .mat-button-wrapper>*,.mat-stroked-button .mat-button-wrapper>*,.mat-raised-button .mat-button-wrapper>*,.mat-icon-button .mat-button-wrapper>*,.mat-fab .mat-button-wrapper>*,.mat-mini-fab .mat-button-wrapper>*{vertical-align:middle}.mat-form-field:not(.mat-form-field-appearance-legacy) .mat-form-field-prefix .mat-icon-button,.mat-form-field:not(.mat-form-field-appearance-legacy) .mat-form-field-suffix .mat-icon-button{display:inline-flex;justify-content:center;align-items:center;font-size:inherit;width:2.5em;height:2.5em}.mat-flat-button::before,.mat-raised-button::before,.mat-fab::before,.mat-mini-fab::before{margin:calc(calc(var(--mat-focus-indicator-border-width, 3px) + 2px) * -1)}.mat-stroked-button::before{margin:calc(calc(var(--mat-focus-indicator-border-width, 3px) + 3px) * -1)}.cdk-high-contrast-active .mat-button,.cdk-high-contrast-active .mat-flat-button,.cdk-high-contrast-active .mat-raised-button,.cdk-high-contrast-active .mat-icon-button,.cdk-high-contrast-active .mat-fab,.cdk-high-contrast-active .mat-mini-fab{outline:solid 1px}.mat-datepicker-toggle .mat-mdc-button-base{width:40px;height:40px;padding:8px 0}.mat-datepicker-actions .mat-button-base+.mat-button-base{margin-left:8px}[dir=rtl] .mat-datepicker-actions .mat-button-base+.mat-button-base{margin-left:0;margin-right:8px}

mat-icon,mat-icon.mat-primary,mat-icon.mat-accent,mat-icon.mat-warn{color:var(--mat-icon-color)}.mat-icon{-webkit-user-select:none;user-select:none;background-repeat:no-repeat;display:inline-block;fill:currentColor;height:24px;width:24px;overflow:hidden}.mat-icon.mat-icon-inline{font-size:inherit;height:inherit;line-height:inherit;width:inherit}.mat-icon.mat-ligature-font[fontIcon]::before{content:attr(fontIcon)}[dir=rtl] .mat-icon-rtl-mirror{transform:scale(-1, 1)}.mat-form-field:not(.mat-form-field-appearance-legacy) .mat-form-field-prefix .mat-icon,.mat-form-field:not(.mat-form-field-appearance-legacy) .mat-form-field-suffix .mat-icon{display:block}.mat-form-field:not(.mat-form-field-appearance-legacy) .mat-form-field-prefix .mat-icon-button .mat-icon,.mat-form-field:not(.mat-form-field-appearance-legacy) .mat-form-field-suffix .mat-icon-button .mat-icon{margin:auto}

#welcome-section #welcome-banner{color:#fff;width:calc(100% - 60px);height:80px;display:flex;flex-direction:row;align-items:center;background:rgb(2,0,90);background:url(/wand/app/worker/assets/general/welcome-banner-BG.svg);justify-content:space-between;padding:0 30px;margin-bottom:30px;border-radius:4px}#welcome-section #welcome-banner img{height:46px;width:46px;vertical-align:middle;margin-right:25px}#welcome-section #welcome-banner label{vertical-align:middle;font-weight:700;font-size:24px}#welcome-section .welcome{color:#2a394f;font-size:21px;font-weight:600}#welcome-section .welcomeDate{font-size:16px;font-weight:600}#add-time-expense-card .grayLabel{display:block;color:#637a89;font-size:14px;font-weight:500;margin-right:5px}.viewAllRequistionsButton{font-weight:700;font-size:14px;color:#0663de}mat-card{padding:30px}     table .mat-header-cell{border:none}     table tr:first-child td.mat-cell{border-top-width:1px;border-top-style:solid;border-top-color:#e8e8e8}     table td.mat-cell:first-child{border-left:1px solid rgb(232,232,232)}     table td.mat-cell:last-child{border-right:1px solid rgb(232,232,232)}     table .th-selection{width:10%}.table-noInformation{min-height:160px;background-color:#f3f5f880}.table-noInformation span{font-size:12px;font-weight:600;color:#2a394f61}.inline-field-label{position:relative;bottom:9px;font-size:14px;font-weight:600;color:#2a394fd9}  .time-expense-tooltip{min-width:250px;width:250px}.travel-related{margin-left:10px;margin-bottom:20px}.loading-engagement{margin-left:60px;margin-bottom:25px}#engagement-table{width:100%;table-layout:auto}#engagement-table tr{cursor:pointer}#engagement-table tr .mat-cell{padding-top:20px;padding-bottom:20px}#engagement-table tr .mat-column-eng_id{width:96px}#engagement-table tr td.mat-column-start_date{width:77px}#engagement-table tr th.mat-column-end_date{padding-right:15px}#engagement-table tr td.mat-column-end_date{width:77px}#pending-time-expense-card{margin-bottom:0}#pending-time-expense-card table td.mat-column-status .status-column-value td.mat-column-end_date{display:flex;gap:5px}#pending-time-expense-card table td.mat-column-status .status-column-value td.mat-column-end_date mat-icon{font-size:18px;height:18px;width:18px}#pending-time-expense-card table th > mat-icon.info-icon{margin-bottom:-12px}.end-date-cell{display:flex;gap:5px}  .status-reason-popover{margin-bottom:10px;font-size:14px;text-align:justify}  .status-reason-popover .mde-popover-content{padding:0!important;margin:0!important;max-width:500px}mat-icon.info-icon{font-size:16px;margin-left:2px;margin-bottom:-10px}

mat-card.announcement-banner-container{display:flex;flex-direction:row;gap:12px;margin-bottom:0}mat-card.announcement-banner-container .heading-container{width:275px;margin-top:5px}mat-card.announcement-banner-container .heading-container .heading{display:flex;flex-direction:row;align-items:center;gap:18px;border-left:2px solid #00B2E3;padding:10px 24px}mat-card.announcement-banner-container .heading-container .heading h3{margin-bottom:0}mat-card.announcement-banner-container .announcements-list{width:800px}mat-card.announcement-banner-container .announcements-list .announcement .title{display:block;margin-bottom:12px;font-size:14px;font-weight:600;color:#2a394f}mat-card.announcement-banner-container .announcements-list .announcement:not(:last-child){margin-bottom:22px}

.mat-card{transition:box-shadow 280ms cubic-bezier(0.4, 0, 0.2, 1);display:block;position:relative;padding:16px;border-radius:4px}.mat-card._mat-animation-noopable{transition:none !important;animation:none !important}.mat-card>.mat-divider-horizontal{position:absolute;left:0;width:100%}[dir=rtl] .mat-card>.mat-divider-horizontal{left:auto;right:0}.mat-card>.mat-divider-horizontal.mat-divider-inset{position:static;margin:0}[dir=rtl] .mat-card>.mat-divider-horizontal.mat-divider-inset{margin-right:0}.cdk-high-contrast-active .mat-card{outline:solid 1px}.mat-card-actions,.mat-card-subtitle,.mat-card-content{display:block;margin-bottom:16px}.mat-card-title{display:block;margin-bottom:8px}.mat-card-actions{margin-left:-8px;margin-right:-8px;padding:8px 0}.mat-card-actions-align-end{display:flex;justify-content:flex-end}.mat-card-image{width:calc(100% + 32px);margin:0 -16px 16px -16px;display:block;overflow:hidden}.mat-card-image img{width:100%}.mat-card-footer{display:block;margin:0 -16px -16px -16px}.mat-card-actions .mat-button,.mat-card-actions .mat-raised-button,.mat-card-actions .mat-stroked-button{margin:0 8px}.mat-card-header{display:flex;flex-direction:row}.mat-card-header .mat-card-title{margin-bottom:12px}.mat-card-header-text{margin:0 16px}.mat-card-avatar{height:40px;width:40px;border-radius:50%;flex-shrink:0;object-fit:cover}.mat-card-title-group{display:flex;justify-content:space-between}.mat-card-sm-image{width:80px;height:80px}.mat-card-md-image{width:112px;height:112px}.mat-card-lg-image{width:152px;height:152px}.mat-card-xl-image{width:240px;height:240px;margin:-8px}.mat-card-title-group>.mat-card-xl-image{margin:-8px 0 8px}@media(max-width: 599px){.mat-card-title-group{margin:0}.mat-card-xl-image{margin-left:0;margin-right:0}}.mat-card>:first-child,.mat-card-content>:first-child{margin-top:0}.mat-card>:last-child:not(.mat-card-footer),.mat-card-content>:last-child:not(.mat-card-footer){margin-bottom:0}.mat-card-image:first-child{margin-top:-16px;border-top-left-radius:inherit;border-top-right-radius:inherit}.mat-card>.mat-card-actions:last-child{margin-bottom:-8px;padding-bottom:0}.mat-card-actions:not(.mat-card-actions-align-end) .mat-button:first-child,.mat-card-actions:not(.mat-card-actions-align-end) .mat-raised-button:first-child,.mat-card-actions:not(.mat-card-actions-align-end) .mat-stroked-button:first-child{margin-left:0;margin-right:0}.mat-card-actions-align-end .mat-button:last-child,.mat-card-actions-align-end .mat-raised-button:last-child,.mat-card-actions-align-end .mat-stroked-button:last-child{margin-left:0;margin-right:0}.mat-card-title:not(:first-child),.mat-card-subtitle:not(:first-child){margin-top:-4px}.mat-card-header .mat-card-subtitle:not(:first-child){margin-top:-8px}.mat-card>.mat-card-xl-image:first-child{margin-top:-8px}.mat-card>.mat-card-xl-image:last-child{margin-bottom:-8px}

mat-table{display:block}mat-header-row{min-height:56px}mat-row,mat-footer-row{min-height:48px}mat-row,mat-header-row,mat-footer-row{display:flex;border-width:0;border-bottom-width:1px;border-style:solid;align-items:center;box-sizing:border-box}mat-cell:first-of-type,mat-header-cell:first-of-type,mat-footer-cell:first-of-type{padding-left:24px}[dir=rtl] mat-cell:first-of-type:not(:only-of-type),[dir=rtl] mat-header-cell:first-of-type:not(:only-of-type),[dir=rtl] mat-footer-cell:first-of-type:not(:only-of-type){padding-left:0;padding-right:24px}mat-cell:last-of-type,mat-header-cell:last-of-type,mat-footer-cell:last-of-type{padding-right:24px}[dir=rtl] mat-cell:last-of-type:not(:only-of-type),[dir=rtl] mat-header-cell:last-of-type:not(:only-of-type),[dir=rtl] mat-footer-cell:last-of-type:not(:only-of-type){padding-right:0;padding-left:24px}mat-cell,mat-header-cell,mat-footer-cell{flex:1;display:flex;align-items:center;overflow:hidden;word-wrap:break-word;min-height:inherit}table.mat-table{border-spacing:0}tr.mat-header-row{height:56px}tr.mat-row,tr.mat-footer-row{height:48px}th.mat-header-cell{text-align:left}[dir=rtl] th.mat-header-cell{text-align:right}th.mat-header-cell,td.mat-cell,td.mat-footer-cell{padding:0;border-bottom-width:1px;border-bottom-style:solid}th.mat-header-cell:first-of-type,td.mat-cell:first-of-type,td.mat-footer-cell:first-of-type{padding-left:24px}[dir=rtl] th.mat-header-cell:first-of-type:not(:only-of-type),[dir=rtl] td.mat-cell:first-of-type:not(:only-of-type),[dir=rtl] td.mat-footer-cell:first-of-type:not(:only-of-type){padding-left:0;padding-right:24px}th.mat-header-cell:last-of-type,td.mat-cell:last-of-type,td.mat-footer-cell:last-of-type{padding-right:24px}[dir=rtl] th.mat-header-cell:last-of-type:not(:only-of-type),[dir=rtl] td.mat-cell:last-of-type:not(:only-of-type),[dir=rtl] td.mat-footer-cell:last-of-type:not(:only-of-type){padding-right:0;padding-left:24px}.mat-table-sticky{position:sticky !important}.mat-table-fixed-layout{table-layout:fixed}

.mat-progress-spinner{display:block;position:relative;overflow:hidden}.mat-progress-spinner svg{position:absolute;transform:rotate(-90deg);top:0;left:0;transform-origin:center;overflow:visible}.mat-progress-spinner circle{fill:rgba(0,0,0,0);transition:stroke-dashoffset 225ms linear}.cdk-high-contrast-active .mat-progress-spinner circle{stroke:CanvasText}.mat-progress-spinner[mode=indeterminate] svg{animation:mat-progress-spinner-linear-rotate 2000ms linear infinite}.mat-progress-spinner[mode=indeterminate] circle{transition-property:stroke;animation-duration:4000ms;animation-timing-function:cubic-bezier(0.35, 0, 0.25, 1);animation-iteration-count:infinite}.mat-progress-spinner._mat-animation-noopable svg,.mat-progress-spinner._mat-animation-noopable circle{animation:none;transition:none}@keyframes mat-progress-spinner-linear-rotate{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}@keyframes mat-progress-spinner-stroke-rotate-100{0%{stroke-dashoffset:268.606171575px;transform:rotate(0)}12.5%{stroke-dashoffset:56.5486677px;transform:rotate(0)}12.5001%{stroke-dashoffset:56.5486677px;transform:rotateX(180deg) rotate(72.5deg)}25%{stroke-dashoffset:268.606171575px;transform:rotateX(180deg) rotate(72.5deg)}25.0001%{stroke-dashoffset:268.606171575px;transform:rotate(270deg)}37.5%{stroke-dashoffset:56.5486677px;transform:rotate(270deg)}37.5001%{stroke-dashoffset:56.5486677px;transform:rotateX(180deg) rotate(161.5deg)}50%{stroke-dashoffset:268.606171575px;transform:rotateX(180deg) rotate(161.5deg)}50.0001%{stroke-dashoffset:268.606171575px;transform:rotate(180deg)}62.5%{stroke-dashoffset:56.5486677px;transform:rotate(180deg)}62.5001%{stroke-dashoffset:56.5486677px;transform:rotateX(180deg) rotate(251.5deg)}75%{stroke-dashoffset:268.606171575px;transform:rotateX(180deg) rotate(251.5deg)}75.0001%{stroke-dashoffset:268.606171575px;transform:rotate(90deg)}87.5%{stroke-dashoffset:56.5486677px;transform:rotate(90deg)}87.5001%{stroke-dashoffset:56.5486677px;transform:rotateX(180deg) rotate(341.5deg)}100%{stroke-dashoffset:268.606171575px;transform:rotateX(180deg) rotate(341.5deg)}}

 @keyframes mat-progress-spinner-stroke-rotate-30 {
    0%      { stroke-dashoffset: 59.690260418206066;  transform: rotate(0); }
    12.5%   { stroke-dashoffset: 12.566370614359172;    transform: rotate(0); }
    12.5001%  { stroke-dashoffset: 12.566370614359172;    transform: rotateX(180deg) rotate(72.5deg); }
    25%     { stroke-dashoffset: 59.690260418206066;  transform: rotateX(180deg) rotate(72.5deg); }

    25.0001%   { stroke-dashoffset: 59.690260418206066;  transform: rotate(270deg); }
    37.5%   { stroke-dashoffset: 12.566370614359172;    transform: rotate(270deg); }
    37.5001%  { stroke-dashoffset: 12.566370614359172;    transform: rotateX(180deg) rotate(161.5deg); }
    50%     { stroke-dashoffset: 59.690260418206066;  transform: rotateX(180deg) rotate(161.5deg); }

    50.0001%  { stroke-dashoffset: 59.690260418206066;  transform: rotate(180deg); }
    62.5%   { stroke-dashoffset: 12.566370614359172;    transform: rotate(180deg); }
    62.5001%  { stroke-dashoffset: 12.566370614359172;    transform: rotateX(180deg) rotate(251.5deg); }
    75%     { stroke-dashoffset: 59.690260418206066;  transform: rotateX(180deg) rotate(251.5deg); }

    75.0001%  { stroke-dashoffset: 59.690260418206066;  transform: rotate(90deg); }
    87.5%   { stroke-dashoffset: 12.566370614359172;    transform: rotate(90deg); }
    87.5001%  { stroke-dashoffset: 12.566370614359172;    transform: rotateX(180deg) rotate(341.5deg); }
    100%    { stroke-dashoffset: 59.690260418206066;  transform: rotateX(180deg) rotate(341.5deg); }
  }

.mde-popover-panel{display:flex;flex-direction:column;max-height:calc(100vh + 48px)}.mde-popover-ripple{position:absolute;top:0;left:0;bottom:0;right:0}.mde-popover-below .mde-popover-direction-arrow{position:absolute;bottom:0;width:0;height:0;border-bottom-width:0!important;z-index:99999}.mde-popover-above .mde-popover-direction-arrow{position:absolute;top:0;width:0;height:0;border-top-width:0!important;z-index:99999}.mde-popover-after .mde-popover-direction-arrow{left:20px}.mde-popover-before .mde-popover-direction-arrow{right:20px}

.mat-toolbar{background:var(--mat-toolbar-container-background-color);color:var(--mat-toolbar-container-text-color)}.mat-toolbar,.mat-toolbar h1,.mat-toolbar h2,.mat-toolbar h3,.mat-toolbar h4,.mat-toolbar h5,.mat-toolbar h6{font-family:var(--mat-toolbar-title-text-font);font-size:var(--mat-toolbar-title-text-size);line-height:var(--mat-toolbar-title-text-line-height);font-weight:var(--mat-toolbar-title-text-weight);letter-spacing:var(--mat-toolbar-title-text-tracking);margin:0}.cdk-high-contrast-active .mat-toolbar{outline:solid 1px}.mat-toolbar .mat-form-field-underline,.mat-toolbar .mat-form-field-ripple,.mat-toolbar .mat-focused .mat-form-field-ripple{background-color:currentColor}.mat-toolbar .mat-form-field-label,.mat-toolbar .mat-focused .mat-form-field-label,.mat-toolbar .mat-select-value,.mat-toolbar .mat-select-arrow,.mat-toolbar .mat-form-field.mat-focused .mat-select-arrow{color:inherit}.mat-toolbar .mat-input-element{caret-color:currentColor}.mat-toolbar .mat-mdc-button-base.mat-mdc-button-base.mat-unthemed{--mdc-text-button-label-text-color: inherit;--mdc-outlined-button-label-text-color: inherit}.mat-toolbar-row,.mat-toolbar-single-row{display:flex;box-sizing:border-box;padding:0 16px;width:100%;flex-direction:row;align-items:center;white-space:nowrap;height:var(--mat-toolbar-standard-height)}@media(max-width: 599px){.mat-toolbar-row,.mat-toolbar-single-row{height:var(--mat-toolbar-mobile-height)}}.mat-toolbar-multiple-rows{display:flex;box-sizing:border-box;flex-direction:column;width:100%;min-height:var(--mat-toolbar-standard-height)}@media(max-width: 599px){.mat-toolbar-multiple-rows{min-height:var(--mat-toolbar-mobile-height)}}

footer{text-align:center;font-size:12px;padding-top:50px;line-height:45px;color:#a2b6d3;text-transform:uppercase;clear:left}

 @keyframes mat-progress-spinner-stroke-rotate-50 {
    0%      { stroke-dashoffset: 119.38052083641213;  transform: rotate(0); }
    12.5%   { stroke-dashoffset: 25.132741228718345;    transform: rotate(0); }
    12.5001%  { stroke-dashoffset: 25.132741228718345;    transform: rotateX(180deg) rotate(72.5deg); }
    25%     { stroke-dashoffset: 119.38052083641213;  transform: rotateX(180deg) rotate(72.5deg); }

    25.0001%   { stroke-dashoffset: 119.38052083641213;  transform: rotate(270deg); }
    37.5%   { stroke-dashoffset: 25.132741228718345;    transform: rotate(270deg); }
    37.5001%  { stroke-dashoffset: 25.132741228718345;    transform: rotateX(180deg) rotate(161.5deg); }
    50%     { stroke-dashoffset: 119.38052083641213;  transform: rotateX(180deg) rotate(161.5deg); }

    50.0001%  { stroke-dashoffset: 119.38052083641213;  transform: rotate(180deg); }
    62.5%   { stroke-dashoffset: 25.132741228718345;    transform: rotate(180deg); }
    62.5001%  { stroke-dashoffset: 25.132741228718345;    transform: rotateX(180deg) rotate(251.5deg); }
    75%     { stroke-dashoffset: 119.38052083641213;  transform: rotateX(180deg) rotate(251.5deg); }

    75.0001%  { stroke-dashoffset: 119.38052083641213;  transform: rotate(90deg); }
    87.5%   { stroke-dashoffset: 25.132741228718345;    transform: rotate(90deg); }
    87.5001%  { stroke-dashoffset: 25.132741228718345;    transform: rotateX(180deg) rotate(341.5deg); }
    100%    { stroke-dashoffset: 119.38052083641213;  transform: rotateX(180deg) rotate(341.5deg); }
  }

.mat-subheader{display:flex;box-sizing:border-box;padding:16px;align-items:center}.mat-list-base .mat-subheader{margin:0}button.mat-list-item,button.mat-list-option{padding:0;width:100%;background:none;color:inherit;border:none;outline:inherit;-webkit-tap-highlight-color:rgba(0,0,0,0);text-align:left}[dir=rtl] button.mat-list-item,[dir=rtl] button.mat-list-option{text-align:right}button.mat-list-item::-moz-focus-inner,button.mat-list-option::-moz-focus-inner{border:0}.mat-list-base{padding-top:8px;display:block;-webkit-tap-highlight-color:rgba(0,0,0,0)}.mat-list-base .mat-subheader{height:48px;line-height:16px}.mat-list-base .mat-subheader:first-child{margin-top:-8px}.mat-list-base .mat-list-item,.mat-list-base .mat-list-option{display:block;height:48px;-webkit-tap-highlight-color:rgba(0,0,0,0);width:100%;padding:0}.mat-list-base .mat-list-item .mat-list-item-content,.mat-list-base .mat-list-option .mat-list-item-content{display:flex;flex-direction:row;align-items:center;box-sizing:border-box;padding:0 16px;position:relative;height:inherit}.mat-list-base .mat-list-item .mat-list-item-content-reverse,.mat-list-base .mat-list-option .mat-list-item-content-reverse{display:flex;align-items:center;padding:0 16px;flex-direction:row-reverse;justify-content:space-around}.mat-list-base .mat-list-item .mat-list-item-ripple,.mat-list-base .mat-list-option .mat-list-item-ripple{display:block;top:0;left:0;right:0;bottom:0;position:absolute;pointer-events:none}.mat-list-base .mat-list-item.mat-list-item-with-avatar,.mat-list-base .mat-list-option.mat-list-item-with-avatar{height:56px}.mat-list-base .mat-list-item.mat-2-line,.mat-list-base .mat-list-option.mat-2-line{height:72px}.mat-list-base .mat-list-item.mat-3-line,.mat-list-base .mat-list-option.mat-3-line{height:88px}.mat-list-base .mat-list-item.mat-multi-line,.mat-list-base .mat-list-option.mat-multi-line{height:auto}.mat-list-base .mat-list-item.mat-multi-line .mat-list-item-content,.mat-list-base .mat-list-option.mat-multi-line .mat-list-item-content{padding-top:16px;padding-bottom:16px}.mat-list-base .mat-list-item .mat-list-text,.mat-list-base .mat-list-option .mat-list-text{display:flex;flex-direction:column;flex:auto;box-sizing:border-box;overflow:hidden;padding:0}.mat-list-base .mat-list-item .mat-list-text>*,.mat-list-base .mat-list-option .mat-list-text>*{margin:0;padding:0;font-weight:normal;font-size:inherit}.mat-list-base .mat-list-item .mat-list-text:empty,.mat-list-base .mat-list-option .mat-list-text:empty{display:none}.mat-list-base .mat-list-item.mat-list-item-with-avatar .mat-list-item-content .mat-list-text,.mat-list-base .mat-list-item.mat-list-option .mat-list-item-content .mat-list-text,.mat-list-base .mat-list-option.mat-list-item-with-avatar .mat-list-item-content .mat-list-text,.mat-list-base .mat-list-option.mat-list-option .mat-list-item-content .mat-list-text{padding-right:0;padding-left:16px}[dir=rtl] .mat-list-base .mat-list-item.mat-list-item-with-avatar .mat-list-item-content .mat-list-text,[dir=rtl] .mat-list-base .mat-list-item.mat-list-option .mat-list-item-content .mat-list-text,[dir=rtl] .mat-list-base .mat-list-option.mat-list-item-with-avatar .mat-list-item-content .mat-list-text,[dir=rtl] .mat-list-base .mat-list-option.mat-list-option .mat-list-item-content .mat-list-text{padding-right:16px;padding-left:0}.mat-list-base .mat-list-item.mat-list-item-with-avatar .mat-list-item-content-reverse .mat-list-text,.mat-list-base .mat-list-item.mat-list-option .mat-list-item-content-reverse .mat-list-text,.mat-list-base .mat-list-option.mat-list-item-with-avatar .mat-list-item-content-reverse .mat-list-text,.mat-list-base .mat-list-option.mat-list-option .mat-list-item-content-reverse .mat-list-text{padding-left:0;padding-right:16px}[dir=rtl] .mat-list-base .mat-list-item.mat-list-item-with-avatar .mat-list-item-content-reverse .mat-list-text,[dir=rtl] .mat-list-base .mat-list-item.mat-list-option .mat-list-item-content-reverse .mat-list-text,[dir=rtl] .mat-list-base .mat-list-option.mat-list-item-with-avatar .mat-list-item-content-reverse .mat-list-text,[dir=rtl] .mat-list-base .mat-list-option.mat-list-option .mat-list-item-content-reverse .mat-list-text{padding-right:0;padding-left:16px}.mat-list-base .mat-list-item.mat-list-item-with-avatar.mat-list-option .mat-list-item-content-reverse .mat-list-text,.mat-list-base .mat-list-item.mat-list-item-with-avatar.mat-list-option .mat-list-item-content .mat-list-text,.mat-list-base .mat-list-option.mat-list-item-with-avatar.mat-list-option .mat-list-item-content-reverse .mat-list-text,.mat-list-base .mat-list-option.mat-list-item-with-avatar.mat-list-option .mat-list-item-content .mat-list-text{padding-right:16px;padding-left:16px}.mat-list-base .mat-list-item .mat-list-avatar,.mat-list-base .mat-list-option .mat-list-avatar{flex-shrink:0;width:40px;height:40px;border-radius:50%;object-fit:cover}.mat-list-base .mat-list-item .mat-list-avatar~.mat-divider-inset,.mat-list-base .mat-list-option .mat-list-avatar~.mat-divider-inset{margin-left:72px;width:calc(100% - 72px)}[dir=rtl] .mat-list-base .mat-list-item .mat-list-avatar~.mat-divider-inset,[dir=rtl] .mat-list-base .mat-list-option .mat-list-avatar~.mat-divider-inset{margin-left:auto;margin-right:72px}.mat-list-base .mat-list-item .mat-list-icon,.mat-list-base .mat-list-option .mat-list-icon{flex-shrink:0;width:24px;height:24px;font-size:24px;box-sizing:content-box;border-radius:50%;padding:4px}.mat-list-base .mat-list-item .mat-list-icon~.mat-divider-inset,.mat-list-base .mat-list-option .mat-list-icon~.mat-divider-inset{margin-left:64px;width:calc(100% - 64px)}[dir=rtl] .mat-list-base .mat-list-item .mat-list-icon~.mat-divider-inset,[dir=rtl] .mat-list-base .mat-list-option .mat-list-icon~.mat-divider-inset{margin-left:auto;margin-right:64px}.mat-list-base .mat-list-item .mat-divider,.mat-list-base .mat-list-option .mat-divider{position:absolute;bottom:0;left:0;width:100%;margin:0}[dir=rtl] .mat-list-base .mat-list-item .mat-divider,[dir=rtl] .mat-list-base .mat-list-option .mat-divider{margin-left:auto;margin-right:0}.mat-list-base .mat-list-item .mat-divider.mat-divider-inset,.mat-list-base .mat-list-option .mat-divider.mat-divider-inset{position:absolute}.mat-list-base[dense]{padding-top:4px;display:block}.mat-list-base[dense] .mat-subheader{height:40px;line-height:8px}.mat-list-base[dense] .mat-subheader:first-child{margin-top:-4px}.mat-list-base[dense] .mat-list-item,.mat-list-base[dense] .mat-list-option{display:block;height:40px;-webkit-tap-highlight-color:rgba(0,0,0,0);width:100%;padding:0}.mat-list-base[dense] .mat-list-item .mat-list-item-content,.mat-list-base[dense] .mat-list-option .mat-list-item-content{display:flex;flex-direction:row;align-items:center;box-sizing:border-box;padding:0 16px;position:relative;height:inherit}.mat-list-base[dense] .mat-list-item .mat-list-item-content-reverse,.mat-list-base[dense] .mat-list-option .mat-list-item-content-reverse{display:flex;align-items:center;padding:0 16px;flex-direction:row-reverse;justify-content:space-around}.mat-list-base[dense] .mat-list-item .mat-list-item-ripple,.mat-list-base[dense] .mat-list-option .mat-list-item-ripple{display:block;top:0;left:0;right:0;bottom:0;position:absolute;pointer-events:none}.mat-list-base[dense] .mat-list-item.mat-list-item-with-avatar,.mat-list-base[dense] .mat-list-option.mat-list-item-with-avatar{height:48px}.mat-list-base[dense] .mat-list-item.mat-2-line,.mat-list-base[dense] .mat-list-option.mat-2-line{height:60px}.mat-list-base[dense] .mat-list-item.mat-3-line,.mat-list-base[dense] .mat-list-option.mat-3-line{height:76px}.mat-list-base[dense] .mat-list-item.mat-multi-line,.mat-list-base[dense] .mat-list-option.mat-multi-line{height:auto}.mat-list-base[dense] .mat-list-item.mat-multi-line .mat-list-item-content,.mat-list-base[dense] .mat-list-option.mat-multi-line .mat-list-item-content{padding-top:16px;padding-bottom:16px}.mat-list-base[dense] .mat-list-item .mat-list-text,.mat-list-base[dense] .mat-list-option .mat-list-text{display:flex;flex-direction:column;flex:auto;box-sizing:border-box;overflow:hidden;padding:0}.mat-list-base[dense] .mat-list-item .mat-list-text>*,.mat-list-base[dense] .mat-list-option .mat-list-text>*{margin:0;padding:0;font-weight:normal;font-size:inherit}.mat-list-base[dense] .mat-list-item .mat-list-text:empty,.mat-list-base[dense] .mat-list-option .mat-list-text:empty{display:none}.mat-list-base[dense] .mat-list-item.mat-list-item-with-avatar .mat-list-item-content .mat-list-text,.mat-list-base[dense] .mat-list-item.mat-list-option .mat-list-item-content .mat-list-text,.mat-list-base[dense] .mat-list-option.mat-list-item-with-avatar .mat-list-item-content .mat-list-text,.mat-list-base[dense] .mat-list-option.mat-list-option .mat-list-item-content .mat-list-text{padding-right:0;padding-left:16px}[dir=rtl] .mat-list-base[dense] .mat-list-item.mat-list-item-with-avatar .mat-list-item-content .mat-list-text,[dir=rtl] .mat-list-base[dense] .mat-list-item.mat-list-option .mat-list-item-content .mat-list-text,[dir=rtl] .mat-list-base[dense] .mat-list-option.mat-list-item-with-avatar .mat-list-item-content .mat-list-text,[dir=rtl] .mat-list-base[dense] .mat-list-option.mat-list-option .mat-list-item-content .mat-list-text{padding-right:16px;padding-left:0}.mat-list-base[dense] .mat-list-item.mat-list-item-with-avatar .mat-list-item-content-reverse .mat-list-text,.mat-list-base[dense] .mat-list-item.mat-list-option .mat-list-item-content-reverse .mat-list-text,.mat-list-base[dense] .mat-list-option.mat-list-item-with-avatar .mat-list-item-content-reverse .mat-list-text,.mat-list-base[dense] .mat-list-option.mat-list-option .mat-list-item-content-reverse .mat-list-text{padding-left:0;padding-right:16px}[dir=rtl] .mat-list-base[dense] .mat-list-item.mat-list-item-with-avatar .mat-list-item-content-reverse .mat-list-text,[dir=rtl] .mat-list-base[dense] .mat-list-item.mat-list-option .mat-list-item-content-reverse .mat-list-text,[dir=rtl] .mat-list-base[dense] .mat-list-option.mat-list-item-with-avatar .mat-list-item-content-reverse .mat-list-text,[dir=rtl] .mat-list-base[dense] .mat-list-option.mat-list-option .mat-list-item-content-reverse .mat-list-text{padding-right:0;padding-left:16px}.mat-list-base[dense] .mat-list-item.mat-list-item-with-avatar.mat-list-option .mat-list-item-content-reverse .mat-list-text,.mat-list-base[dense] .mat-list-item.mat-list-item-with-avatar.mat-list-option .mat-list-item-content .mat-list-text,.mat-list-base[dense] .mat-list-option.mat-list-item-with-avatar.mat-list-option .mat-list-item-content-reverse .mat-list-text,.mat-list-base[dense] .mat-list-option.mat-list-item-with-avatar.mat-list-option .mat-list-item-content .mat-list-text{padding-right:16px;padding-left:16px}.mat-list-base[dense] .mat-list-item .mat-list-avatar,.mat-list-base[dense] .mat-list-option .mat-list-avatar{flex-shrink:0;width:36px;height:36px;border-radius:50%;object-fit:cover}.mat-list-base[dense] .mat-list-item .mat-list-avatar~.mat-divider-inset,.mat-list-base[dense] .mat-list-option .mat-list-avatar~.mat-divider-inset{margin-left:68px;width:calc(100% - 68px)}[dir=rtl] .mat-list-base[dense] .mat-list-item .mat-list-avatar~.mat-divider-inset,[dir=rtl] .mat-list-base[dense] .mat-list-option .mat-list-avatar~.mat-divider-inset{margin-left:auto;margin-right:68px}.mat-list-base[dense] .mat-list-item .mat-list-icon,.mat-list-base[dense] .mat-list-option .mat-list-icon{flex-shrink:0;width:20px;height:20px;font-size:20px;box-sizing:content-box;border-radius:50%;padding:4px}.mat-list-base[dense] .mat-list-item .mat-list-icon~.mat-divider-inset,.mat-list-base[dense] .mat-list-option .mat-list-icon~.mat-divider-inset{margin-left:60px;width:calc(100% - 60px)}[dir=rtl] .mat-list-base[dense] .mat-list-item .mat-list-icon~.mat-divider-inset,[dir=rtl] .mat-list-base[dense] .mat-list-option .mat-list-icon~.mat-divider-inset{margin-left:auto;margin-right:60px}.mat-list-base[dense] .mat-list-item .mat-divider,.mat-list-base[dense] .mat-list-option .mat-divider{position:absolute;bottom:0;left:0;width:100%;margin:0}[dir=rtl] .mat-list-base[dense] .mat-list-item .mat-divider,[dir=rtl] .mat-list-base[dense] .mat-list-option .mat-divider{margin-left:auto;margin-right:0}.mat-list-base[dense] .mat-list-item .mat-divider.mat-divider-inset,.mat-list-base[dense] .mat-list-option .mat-divider.mat-divider-inset{position:absolute}.mat-nav-list a{text-decoration:none;color:inherit}.mat-nav-list .mat-list-item{cursor:pointer;outline:none}mat-action-list .mat-list-item{cursor:pointer;outline:inherit}.mat-list-option:not(.mat-list-item-disabled){cursor:pointer;outline:none}.mat-list-item-disabled{pointer-events:none}.cdk-high-contrast-active .mat-list-item-disabled{opacity:.5}.cdk-high-contrast-active :host .mat-list-item-disabled{opacity:.5}.cdk-high-contrast-active .mat-list-option:hover,.cdk-high-contrast-active .mat-nav-list .mat-list-item:hover,.cdk-high-contrast-active mat-action-list .mat-list-item:hover{outline:dotted 1px;z-index:1}.cdk-high-contrast-active .mat-listk-high-contrast-active .mat-list-single-selected-option::after{content:"";position:absolute;top:50%;right:16px;transform:translateY(-50%);width:10px;height:0;border-bottom:solid 10px;border-radius:10px}.cdk-high-contrast-active [dir=rtl] .mat-list-single-selected-option::after{right:auto;left:16px}@media(hover: none){.mat-list-option:not(.mat-list-single-selected-option):not(.mat-list-item-disabled):hover,.mat-nav-list .mat-list-item:not(.mat-list-item-disabled):hover,.mat-action-list .mat-list-item:not(.mat-list-item-disabled):hover{background:none}}

mat-card-title{margin-bottom:15px}main, section{width:100%}form{width:100%}mat-form-field{width:100%}  .time-expense-tooltip{min-width:250px;width:250px}#main-container{display:flex;flex-direction:row;gap:50px}#main-container #left-container{display:flex;flex-direction:column;gap:30px;width:100%}#main-container #left-container .mat-chip-list-wrapper{max-height:160px;overflow:auto}#main-container #left-container .typeChips mat-chip:first-letter{text-transform:capitalize}#main-container #left-container .job-title{margin-bottom:5px;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}#main-container #right-container{display:flex;flex-direction:column;justify-content:space-between;height:100%}#main-container #right-container, #main-container #right-container > *, #main-container #right-container mat-form-field{width:100%}#main-container #right-container > div > span{max-height:50%}#main-container #right-container #button-row{width:100%}#main-container #right-container #button-row align button .expense-label{vertical-align:top}#main-container #right-container #date-other-container{margin-top:8px}#engagement-details-section{display:flex;flex-wrap:wrap;gap:50px;width:100%;background:rgba(41,63,150,.04);padding:30px 12px;position:relative;top:-30px;margin-top:4px;box-sizing:border-box}#travel-related-toggle{margin-left:10px;margin-bottom:20px;margin-top:20px}.loading-engagement{margin-left:60px;margin-bottom:25px}.error-banner{background:rgba(192,57,57,.07);border-radius:4px;padding:15px;margin-top:20px}.error-banner mat-icon{margin-right:5px;color:#c03939;vertical-align:middle}#not-worked-toggle{margin-right:3px}.not-work-toggle-span{margin-bottom:10px}.not-work-toggle-field{float:right;padding-top:3px;padding-left:3px}#not-worked-toggle .mat-slide-toggle-content{white-space:pre-line}#type-container{height:70.5px}  .job-title-tooltip{max-width:unset!important;width:215px;position:relative;left:50px}#add-time-expense-card{margin-bottom:0}

.mat-chip{position:relative;box-sizing:border-box;-webkit-tap-highlight-color:rgba(0,0,0,0);border:none;-webkit-appearance:none;-moz-appearance:none}.mat-chip::before{margin:calc(calc(var(--mat-focus-indicator-border-width, 3px) + 2px) * -1)}.mat-standard-chip{transition:box-shadow 280ms cubic-bezier(0.4, 0, 0.2, 1);display:inline-flex;padding:7px 12px;border-radius:16px;align-items:center;cursor:default;min-height:32px;height:1px}.mat-standard-chip._mat-animation-noopable{transition:none !important;animation:none !important}.mat-standard-chip .mat-chip-remove{border:none;-webkit-appearance:none;-moz-appearance:none;padding:0;background:none}.mat-standard-chip .mat-chip-remove.mat-icon,.mat-standard-chip .mat-chip-remove .mat-icon{width:18px;height:18px;font-size:18px}.mat-standard-chip::after{top:0;left:0;right:0;bottom:0;position:absolute;border-radius:inherit;opacity:0;content:"";pointer-events:none;transition:opacity 200ms cubic-bezier(0.35, 0, 0.25, 1)}.mat-standard-chip:hover::after{opacity:.12}.mat-standard-chip:focus{outline:none}.mat-standard-chip:focus::after{opacity:.16}.cdk-high-contrast-active .mat-standard-chip{outline:solid 1px}.cdk-high-contrast-active .mat-standard-chip.mat-chip-selected{outline-width:3px}.mat-standard-chip.mat-chip-disabled::after{opacity:0}.mat-standard-chip.mat-chip-disabled .mat-chip-remove,.mat-standard-chip.mat-chip-disabled .mat-chip-trailing-icon{cursor:default}.mat-standard-chip.mat-chip-with-trailing-icon.mat-chip-with-avatar,.mat-standard-chip.mat-chip-with-avatar{padding-top:0;padding-bottom:0}.mat-standard-chip.mat-chip-with-trailing-icon.mat-chip-with-avatar{padding-right:8px;padding-left:0}[dir=rtl] .mat-standard-chip.mat-chip-with-trailing-icon.mat-chip-with-avatar{padding-left:8px;padding-right:0}.mat-standard-chip.mat-chip-with-trailing-icon{padding-top:7px;padding-bottom:7px;padding-right:8px;padding-left:12px}[dir=rtl] .mat-standard-chip.mat-chip-with-trailing-icon{padding-left:8px;padding-right:12px}.mat-standard-chip.mat-chip-with-avatar{padding-left:0;padding-right:12px}[dir=rtl] .mat-standard-chip.mat-chip-with-avatar{padding-right:0;padding-left:12px}.mat-standard-chip .mat-chip-avatar{width:24px;height:24px;margin-right:8px;margin-left:4px}[dir=rtl] .mat-standard-chip .mat-chip-avatar{margin-left:8px;margin-right:4px}.mat-standard-chip .mat-chip-remove,.mat-standard-chip .mat-chip-trailing-icon{width:18px;height:18px;cursor:pointer}.mat-standard-chip .mat-chip-remove,.mat-standard-chip .mat-chip-trailing-icon{margin-left:8px;margin-right:0}[dir=rtl] .mat-standard-chip .mat-chip-remove,[dir=rtl] .mat-standard-chip .mat-chip-trailing-icon{margin-right:8px;margin-left:0}.mat-chip-ripple{top:0;left:0;right:0;bottom:0;position:absolute;pointer-events:none;border-radius:inherit;overflow:hidden;transform:translateZ(0)}.mat-chip-list-wrapper{display:flex;flex-direction:row;flex-wrap:wrap;align-items:center;margin:-4px}.mat-chip-list-wrapper input.mat-input-element,.mat-chip-list-wrapper .mat-standard-chip{margin:4px}.mat-chip-list-stacked .mat-chip-list-wrapper{flex-direction:column;align-items:flex-start}.mat-chip-list-stacked .mat-chip-list-wrapper .mat-standard-chip{width:100%}.mat-chip-avatar{border-radius:50%;justify-content:center;align-items:center;display:flex;overflow:hidden;object-fit:cover}input.mat-chip-input{width:150px;margin:4px;flex:1 0 150px}

.mat-form-field{display:inline-block;position:relative;text-align:left}[dir=rtl] .mat-form-field{text-align:right}.mat-form-field-wrapper{position:relative}.mat-form-field-flex{display:inline-flex;align-items:baseline;box-sizing:border-box;width:100%}.mat-form-field-prefix,.mat-form-field-suffix{white-space:nowrap;flex:none;position:relative}.mat-form-field-infix{display:block;position:relative;flex:auto;min-width:0;width:180px}.cdk-high-contrast-active .mat-form-field-infix{border-image:linear-gradient(transparent, transparent)}.mat-form-field-label-wrapper{position:absolute;left:0;box-sizing:content-box;width:100%;height:100%;overflow:hidden;pointer-events:none}[dir=rtl] .mat-form-field-label-wrapper{left:auto;right:0}.mat-form-field-label{position:absolute;left:0;font:inherit;pointer-events:none;width:100%;white-space:nowrap;text-overflow:ellipsis;overflow:hidden;transform-origin:0 0;transition:transform 400ms cubic-bezier(0.25, 0.8, 0.25, 1),color 400ms cubic-bezier(0.25, 0.8, 0.25, 1),width 400ms cubic-bezier(0.25, 0.8, 0.25, 1);display:none}[dir=rtl] .mat-form-field-label{transform-origin:100% 0;left:auto;right:0}.cdk-high-contrast-active .mat-form-field-disabled .mat-form-field-label{color:GrayText}.mat-form-field-empty.mat-form-field-label,.mat-form-field-can-float.mat-form-field-should-float .mat-form-field-label{display:block}.mat-form-field-autofill-control:-webkit-autofill+.mat-form-field-label-wrapper .mat-form-field-label{display:none}.mat-form-field-can-float .mat-form-field-autofill-control:-webkit-autofill+.mat-form-field-label-wrapper .mat-form-field-label{display:block;transition:none}.mat-input-server:focus+.mat-form-field-label-wrapper .mat-form-field-label,.mat-input-server[placeholder]:not(:placeholder-shown)+.mat-form-field-label-wrapper .mat-form-field-label{display:none}.mat-form-field-can-float .mat-input-server:focus+.mat-form-field-label-wrapper .mat-form-field-label,.mat-form-field-can-float .mat-input-server[placeholder]:not(:placeholder-shown)+.mat-form-field-label-wrapper .mat-form-field-label{display:block}.mat-form-field-label:not(.mat-form-field-empty){transition:none}.mat-form-field-underline{position:absolute;width:100%;pointer-events:none;transform:scale3d(1, 1.0001, 1)}.mat-form-field-ripple{position:absolute;left:0;width:100%;transform-origin:50%;transform:scaleX(0.5);opacity:0;transition:background-color 300ms cubic-bezier(0.55, 0, 0.55, 0.2)}.mat-form-field.mat-focused .mat-form-field-ripple,.mat-form-field.mat-form-field-invalid .mat-form-field-ripple{opacity:1;transform:none;transition:transform 300ms cubic-bezier(0.25, 0.8, 0.25, 1),opacity 100ms cubic-bezier(0.25, 0.8, 0.25, 1),background-color 300ms cubic-bezier(0.25, 0.8, 0.25, 1)}.mat-form-field-subscript-wrapper{position:absolute;box-sizing:border-box;width:100%;overflow:hidden}.mat-form-field-subscript-wrapper .mat-icon,.mat-form-field-label-wrapper .mat-icon{width:1em;height:1em;font-size:inherit;vertical-align:baseline}.mat-form-field-hint-wrapper{display:flex}.mat-form-field-hint-spacer{flex:1 0 1em}.mat-error{display:block}.mat-form-field-control-wrapper{position:relative}.mat-form-field-hint-end{order:1}.mat-form-field._mat-animation-noopable .mat-form-field-label,.mat-form-field._mat-animation-noopable .mat-form-field-ripple{transition:none}.mat-form-field .mat-form-field-prefix .mat-datepicker-toggle .mat-mdc-button-base,.mat-form-field .mat-form-field-suffix .mat-datepicker-toggle .mat-mdc-button-base{width:40px;height:40px;padding:8px 0}.mat-form-field .mat-datepicker-toggle .mat-mdc-icon-button .mat-icon{font-size:1em;display:inline-block;margin:-2px 0 1px}.mat-form-field-type-mat-date-range-input .mat-form-field-infix{width:200px}.mat-form-field-appearance-legacy .mat-form-field-prefix .mat-datepicker-toggle .mat-mdc-icon-button,.mat-form-field-appearance-legacy .mat-form-field-suffix .mat-datepicker-toggle .mat-mdc-icon-button{font-size:inherit;width:1.5em;height:1.5em;padding:0}.mat-form-field-appearance-legacy .mat-form-field-prefix .mat-datepicker-toggle-default-icon,.mat-form-field-appearance-legacy .mat-form-field-suffix .mat-datepicker-toggle-default-icon{width:1em}.mat-form-field-appearance-legacy .mat-form-field-prefix .mat-datepicker-toggle .mat-mdc-icon-button .mat-icon,.mat-form-field-appearance-legacy .mat-form-field-suffix .mat-datepicker-toggle .mat-mdc-icon-button .mat-icon{line-height:1.5em;margin:0}.mat-form-field .mat-datepicker-toggle .mat-mdc-button-base{vertical-align:middle}.mat-form-field:not(.mat-form-field-appearance-legacy) .mat-datepicker-toggle .mat-mdc-button-base{vertical-align:baseline}

.mat-form-field-appearance-fill .mat-form-field-flex{border-radius:4px 4px 0 0;padding:.75em .75em 0 .75em}.cdk-high-contrast-active .mat-form-field-appearance-fill .mat-form-field-flex{outline:solid 1px}.cdk-high-contrast-active .mat-form-field-appearance-fill.mat-form-field-disabled .mat-form-field-flex{outline-color:GrayText}.cdk-high-contrast-active .mat-form-field-appearance-fill.mat-focused .mat-form-field-flex{outline:dashed 3px}.mat-form-field-appearance-fill .mat-form-field-underline::before{content:"";display:block;position:absolute;bottom:0;height:1px;width:100%}.mat-form-field-appearance-fill .mat-form-field-ripple{bottom:0;height:2px}.cdk-high-contrast-active .mat-form-field-appearance-fill .mat-form-field-ripple{height:0}.mat-form-field-appearance-fill:not(.mat-form-field-disabled) .mat-form-field-flex:hover~.mat-form-field-underline .mat-form-field-ripple{opacity:1;transform:none;transition:opacity 600ms cubic-bezier(0.25, 0.8, 0.25, 1)}.mat-form-field-appearance-fill._mat-animation-noopable:not(.mat-form-field-disabled) .mat-form-field-flex:hover~.mat-form-field-underline .mat-form-field-ripple{transition:none}.mat-form-field-appearance-fill .mat-form-field-subscript-wrapper{padding:0 1em}

.mat-input-element{font:inherit;background:rgba(0,0,0,0);color:currentColor;border:none;outline:none;padding:0;margin:0;width:100%;max-width:100%;vertical-align:bottom;text-align:inherit;box-sizing:content-box}.mat-input-element:-moz-ui-invalid{box-shadow:none}.mat-input-element,.mat-input-element::-webkit-search-cancel-button,.mat-input-element::-webkit-search-decoration,.mat-input-element::-webkit-search-results-button,.mat-input-element::-webkit-search-results-decoration{-webkit-appearance:none}.mat-input-element::-webkit-contacts-auto-fill-button,.mat-input-element::-webkit-caps-lock-indicator,.mat-input-element:not([type=password])::-webkit-credentials-auto-fill-button{visibility:hidden}.mat-input-element[type=date],.mat-input-element[type=datetime],.mat-input-element[type=datetime-local],.mat-input-element[type=month],.mat-input-element[type=week],.mat-input-element[type=time]{line-height:1}.mat-input-element[type=date]::after,.mat-input-element[type=datetime]::after,.mat-input-element[type=datetime-local]::after,.mat-input-element[type=month]::after,.mat-input-element[type=week]::after,.mat-input-element[type=time]::after{
""")

# Header component (fixed at top)
header = html.Header(
    className="fixed top-0 w-full z-50 bg-white shadow-md py-3",  # Increased padding for better spacing
    children=[
        html.Div(
            className="container mx-auto px-4 flex items-center justify-between",  # Added px-4 for side padding
            children=[
                html.A(
                    html.Img(
                        src="https://www.anaconda.com/wp-content/uploads/2024/11/2020_Anaconda_Logo_RGB_Corporate.png",
                        className="h-12"
                    ),
                    href="https://www.anaconda.com"
                ),
                html.Nav(
                    className="flex items-center space-x-1 md:space-x-3",  # Responsive spacing
                    children=[
                        # Products dropdown
                        html.Details(
                            className="relative group",  # Added group for better hover handling
                            children=[
                                html.Summary(
                                    "Products",
                                    className="cursor-pointer px-3 py-2 hover:bg-gray-100 rounded transition-colors"  # Added hover effect
                                ),
                                html.Div(
                                    className="absolute left-0 mt-1 w-56 bg-white rounded-md shadow-lg z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200",  # Better transitions
                                    children=[
                                        html.A("AI PLATFORM", href="#", className="block px-4 py-2 text-sm text-gray-700 font-bold"),
                                        html.A("Platform Overview", href="https://www.anaconda.com/ai-platform", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Trusted Distribution", href="https://www.anaconda.com/ai-platform/trusted-distribution", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Secure Governance", href="https://www.anaconda.com/ai-platform/secure-governance", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Actionable Insights", href="https://www.anaconda.com/ai-platform/actionable-insights", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.Hr(className="my-1"),
                                        html.A("ANACONDA AI PLATFORM", href="#", className="block px-4 py-2 text-sm text-gray-700 font-bold"),
                                        html.A("Get Started", href="https://auth.anaconda.com/ui/login", className="block px-4 py-2 text-sm text-blue-500 hover:bg-gray-100"),
                                        html.A("Get a Demo", href="https://www.anaconda.com/request-a-demo", className="block px-4 py-2 text-sm text-blue-500 hover:bg-gray-100"),
                                        html.Hr(className="my-1"),
                                        html.A("PRICING", href="#", className="block px-4 py-2 text-sm text-gray-700 font-bold"),
                                        html.A("Anaconda Pricing", href="https://www.anaconda.com/pricing", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                    ]
                                )
                            ]
                        ),
                        # Solutions dropdown (same pattern as Products)
                        html.Details(
                            className="relative group",
                            children=[
                                html.Summary(
                                    "Solutions",
                                    className="cursor-pointer px-3 py-2 hover:bg-gray-100 rounded transition-colors"
                                ),
                                html.Div(
                                    className="absolute left-0 mt-1 w-56 bg-white rounded-md shadow-lg z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200",
                                    children=[
                                        html.A("BY INDUSTRY", href="#", className="block px-4 py-2 text-sm text-gray-700 font-bold"),
                                        html.A("All Industries", href="https://www.anaconda.com/industries", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Academia", href="https://www.anaconda.com/industries/education", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Financial", href="https://www.anaconda.com/industries/financial-services", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Government", href="https://www.anaconda.com/industries/government", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Healthcare", href="https://www.anaconda.com/industries/healthcare", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Manufacturing", href="https://www.anaconda.com/industries/manufacturing", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Technology", href="https://www.anaconda.com/industries/technology", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.Hr(className="my-1"),
                                        html.A("PROFESSIONAL SERVICES", href="#", className="block px-4 py-2 text-sm text-gray-700 font-bold"),
                                        html.A("Anaconda Professional Services", href="https://www.anaconda.com/professional-services", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                    ]
                                )
                            ]
                        ),
                        # Resources dropdown
                        html.Details(
                            className="relative group",
                            children=[
                                html.Summary(
                                    "Resources",
                                    className="cursor-pointer px-3 py-2 hover:bg-gray-100 rounded transition-colors"
                                ),
                                html.Div(
                                    className="absolute left-0 mt-1 w-56 bg-white rounded-md shadow-lg z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200",
                                    children=[
                                        html.A("RESOURCE CENTER", href="#", className="block px-4 py-2 text-sm text-gray-700 font-bold"),
                                        html.A("All Resources", href="https://www.anaconda.com/resources", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Topics", href="https://www.anaconda.com/topics", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Blog", href="https://www.anaconda.com/blog", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Guides", href="https://www.anaconda.com/guides", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Webinars", href="https://www.anaconda.com/recources/webinar", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Podcast", href="https://www.anaconda.com/resources/podcast", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Whitepapers", href="https://www.anaconda.com/resources/whitepaper", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.Hr(className="my-1"),
                                        html.A("FOR USERS", href="#", className="block px-4 py-2 text-sm text-gray-700 font-bold"),
                                        html.A("Download Distribution", href="https://www.anaconda.com/download", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Docs", href="/docs/main", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Support Center", href="https://anaconda.com/app/support-center", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Community", href="https://forum.anaconda.com/", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Anaconda Learning", href="https://www.anaconda.com/learning", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                    ]
                                )
                            ]
                        ),
                        # Company dropdown
                        html.Details(
                            className="relative group",
                            children=[
                                html.Summary(
                                    "Company",
                                    className="cursor-pointer px-3 py-2 hover:bg-gray-100 rounded transition-colors"
                                ),
                                html.Div(
                                    className="absolute left-0 mt-1 w-56 bg-white rounded-md shadow-lg z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200",
                                    children=[
                                        html.A("COMPANY", href="#", className="block px-4 py-2 text-sm text-gray-700 font-bold"),
                                        html.A("About Anaconda", href="https://www.anaconda.com/about-us", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Leadership", href="https://www.anaconda.com/about-us/leadership", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Our Open-Source Commitment", href="https://www.anaconda.com/our-open-source-commitment", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Newsroom", href="https://www.anaconda.com/newsroom", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Press Releases", href="https://www.anaconda.com/press", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Careers", href="https://www.anaconda.com/about-us/careers", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.Hr(className="my-1"),
                                        html.A("PARTNER NETWORK", href="#", className="block px-4 py-2 text-sm text-gray-700 font-bold"),
                                        html.A("Partners", href="https://www.anaconda.com/partners", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Technology Partners", href="https://www.anaconda.com/partners/technology", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Channels and Services Partners", href="https://www.anaconda.com/partners/channel-and-services", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Become a Partner", href="https://www.anaconda.com/partners/become-a-partner", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.Hr(className="my-1"),
                                        html.A("CONTACT", href="#", className="block px-4 py-2 text-sm text-gray-700 font-bold"),
                                        html.A("Contact Us", href="https://www.anaconda.com/contact", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                    ]
                                )
                            ]
                        ),
                        # Buttons with better spacing
                        html.A(
                            "Free Download",
                            href="https://www.anaconda.com/download",
                            className="bg-blue-500 text-white rounded px-4 py-2 mx-1 hover:bg-blue-600 transition-colors"
                        ),
                        html.A(
                            "Sign In",
                            href="https://auth.anaconda.com/ui/login",
                            className="text-blue-500 border border-blue-500 rounded px-4 py-2 mx-1 hover:bg-blue-50 transition-colors"
                        ),
                        html.A(
                            "Get Demo",
                            href="https://www.anaconda.com/request-a-demo",
                            className="bg-blue-500 text-white rounded px-4 py-2 mx-1 hover:bg-blue-600 transition-colors"
                        ),
                    ]
                )
            ]
        )
    ]
)

# Left sidebar component (sticky with proper height calculation)
left_sidebar = html.Div(
    className="fixed top-16 left-0 h-[calc(100vh-4rem)] bg-gray-100 p-5 overflow-y-auto shadow-lg w-64 transition-all duration-300 z-40",  # Fixed positioning with proper height
    children=[
        html.H4("Navigation", className="text-lg font-bold mb-4"),
        html.Nav(
            className="flex flex-col space-y-1",  # Reduced space for tighter layout
            children=[
                html.A("Dashboard", href="#", className="text-gray-700 hover:bg-gray-200 px-4 py-2 rounded transition-colors"),
                html.A("Projects", href="#", className="text-gray-700 hover:bg-gray-200 px-4 py-2 rounded transition-colors"),
                html.A("Environments", href="#", className="text-gray-700 hover:bg-gray-200 px-4 py-2 rounded transition-colors"),
                html.A("Packages", href="#", className="text-gray-700 hover:bg-gray-200 px-4 py-2 rounded transition-colors"),
                html.A("Channels", href="#", className="text-gray-700 hover:bg-gray-200 px-4 py-2 rounded transition-colors"),
                html.A("Settings", href="#", className="text-gray-700 hover:bg-gray-200 px-4 py-2 rounded transition-colors"),
            ]
        ),
        html.Hr(className="my-4"),
        html.H5("Quick Links", className="text-md font-bold mt-4 mb-3"),
        html.Nav(
            className="flex flex-col space-y-1",
            children=[
                html.A("Documentation", href="https://docs.anaconda.com/", className="text-gray-700 hover:bg-gray-200 px-4 py-2 rounded transition-colors"),
                html.A("Community", href="https://forum.anaconda.com/", className="text-gray-700 hover:bg-gray-200 px-4 py-2 rounded transition-colors"),
                html.A("Support", href="https://anaconda.com/app/support-center", className="text-gray-700 hover:bg-gray-200 px-4 py-2 rounded transition-colors"),
            ]
        )
    ]
)

# Main content with proper offset for header and sidebar
main_content = html.Div(
    className="ml-64 pt-16 p-6 flex-grow min-h-screen bg-gray-50",  # Added background and proper offsets
    children=[
        html.Div(
            className="max-w-7xl mx-auto",  # Centered content container
            children=[
                html.Div(
                    className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8",  # Better gap spacing
                    children=[
                        # Left card with hover effect
                        html.Div(
                            className="bg-white rounded-lg shadow-md flex flex-col hover:shadow-lg transition-shadow duration-300",
                            children=[
                                html.Div(
                                    "Anaconda Distribution",
                                    className="bg-blue-500 text-white p-4 rounded-t-lg font-bold"
                                ),
                                html.Div(
                                    className="p-5 flex-grow",  # More padding for content
                                    children=[
                                        html.H4("Python Data Science Platform", className="text-xl font-bold mb-3"),
                                        html.P(
                                            "Anaconda Distribution is the easiest way to perform Python/R data science "
                                            "and machine learning on Linux, Windows, and Mac OS X.",
                                            className="text-gray-700 mb-5"
                                        ),
                                        html.A(
                                            "Download Now",
                                            href="https://www.anaconda.com/download",
                                            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors inline-block"
                                        ),
                                    ]
                                ),
                                html.Div(
                                    "Over 20 million users worldwide",
                                    className="bg-gray-50 p-4 rounded-b-lg text-sm text-gray-600 border-t border-gray-100"  # Subtle border
                                ),
                            ]
                        ),
                        # Right card
                        html.Div(
                            className="bg-white rounded-lg shadow-md flex flex-col hover:shadow-lg transition-shadow duration-300",
                            children=[
                                html.Div(
                                    "Anaconda Professional",
                                    className="bg-green-500 text-white p-4 rounded-t-lg font-bold"
                                ),
                                html.Div(
                                    className="p-5 flex-grow",
                                    children=[
                                        html.H4("Enterprise-Grade Python", className="text-xl font-bold mb-3"),
                                        html.P(
                                            "Anaconda Professional provides additional features for enterprise users "
                                            "including commercial licenses, prioritized packages, and enhanced security.",
                                            className="text-gray-700 mb-5"
                                        ),
                                        html.A(
                                            "Learn More",
                                            href="https://www.anaconda.com/products/individual",
                                            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition-colors inline-block"
                                        ),
                                    ]
                                ),
                                html.Div(
                                    "Trusted by Fortune 500 companies",
                                    className="bg-gray-50 p-4 rounded-b-lg text-sm text-gray-600 border-t border-gray-100"
                                ),
                            ]
                        ),
                    ]
                ),
                # Additional row with some sample content
                html.Div(
                    className="prose max-w-none bg-white p-6 rounded-lg shadow-sm",  # Added background and padding
                    children=[
                        dcc.Markdown("""
                        ### About Anaconda
                        Anaconda is the birthplace of Python data science. We are a movement of data scientists, 
                        data-driven enterprises, and open source communities.
                        """)
                    ]
                )
            ]
        )
    ]
)

# App layout with proper structure
app.layout = html.Div(
    children=[
        html.Script(src="https://cdn.tailwindcss.com"),
        # Custom Tailwind configuration for better defaults
        html.Script("""
            tailwind.config = {
                theme: {
                    extend: {
                        colors: {
                            primary: '#1E88E5',
                            secondary: '#43A047',
                        },
                        fontFamily: {
                            sans: ['Inter', 'system-ui', 'sans-serif'],
                        },
                    }
                }
            }
        """),
        # 添加额外的CSS样式
        additional_styles,
        header,
        left_sidebar,
        main_content
    ]
)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=9070)
