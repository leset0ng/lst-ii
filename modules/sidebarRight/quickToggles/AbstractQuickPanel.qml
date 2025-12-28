import QtQuick
import qs.modules.common
import qs.modules.common.functions

Rectangle {
    id: root

    property bool editMode: false

    radius: Appearance.rounding.normal
    color: Appearance.auroraEverywhere ? Appearance.aurora.colSubSurface : Appearance.colors.colLayer1

    signal openAudioOutputDialog()
    signal openAudioInputDialog()
    signal openBluetoothDialog()
    signal openNightLightDialog()
    signal openWifiDialog()
}
