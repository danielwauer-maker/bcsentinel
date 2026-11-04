controladdin "BCSentinel Scan Visual"
{
    RequestedHeight = 800;
    MinimumHeight = 700;
    MaximumHeight = 1100;
    RequestedWidth = 960;
    MinimumWidth = 320;
    MaximumWidth = 2000;
    HorizontalStretch = true;
    VerticalStretch = false;

    Scripts = './js/scanvisual.js';
    StartupScript = './js/scanvisual-startup.js';
    StyleSheets = './css/scanvisual.css';

    procedure SetScanData(JsonData: Text);
    event ControlReady();
}