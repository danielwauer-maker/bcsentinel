controladdin "BCSentinel Scan Visual"
{
    RequestedHeight = 630;
    MinimumHeight = 420;
    MaximumHeight = 900;
    RequestedWidth = 960;
    MinimumWidth = 320;
    MaximumWidth = 2000;
    HorizontalStretch = true;
    VerticalStretch = false;

    StartupScript = './js/scanvisual.js';
    StyleSheets = './css/scanvisual.css';

    procedure SetScanData(JsonData: Text);
    event ControlReady();
}