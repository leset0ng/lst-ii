import qs.modules.common
import qs.modules.common.widgets
import QtQuick
import QtQuick.Layouts

RippleButton {
    id: button
    property string day
    property int isToday
    property bool bold
    property bool isHeader: false  // True for weekday labels (Mon, Tue, etc.)

    Layout.fillWidth: false
    Layout.fillHeight: false
    implicitWidth: 38; 
    implicitHeight: 38;

    toggled: (isToday == 1) && !isHeader  // Headers don't get toggled background
    buttonRadius: Appearance.rounding.small
    
    contentItem: StyledText {
        anchors.fill: parent
        text: day
        horizontalAlignment: Text.AlignHCenter
        font.weight: bold ? Font.DemiBold : Font.Normal
        // isHeader + isToday: use same color as toggled button background (colPrimary)
        // isToday (not header): white text on primary background
        // normal day: standard text color
        // other month days: muted color
        color: isHeader && (isToday == 1) ? Appearance.colors.colPrimary :
               (isToday == 1) ? Appearance.colors.colOnPrimary : 
               (isToday == 0) ? Appearance.colors.colOnLayer1 : 
               Appearance.colors.colOutlineVariant

        Behavior on color {
            animation: Appearance.animation.elementMoveFast.colorAnimation.createObject(this)
        }
    }
}

