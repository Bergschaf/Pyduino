//
// Created by Christian on 25.09.2022.
//

#include "Arduino.hpp"
#include <windows.h>
#include <cwchar>
#define MAX_VALUE_LENGTH 255

void getUSBSerialList()
{

    HKEY hKey;
    //check if we can read registry
    INT dwRegOPenKey = RegOpenKeyEx(HKEY_LOCAL_MACHINE, _T("SYSTEM\\CurrentControlSet\\Services\\usbser\\Enum"), 0, KEY_READ, &hKey);
    if(dwRegOPenKey != ERROR_SUCCESS) return 0;


    DWORD type=REG_DWORD, size=0, USBser_count = 0; // a place for RegQueryValueEx to write back to
    DWORD dwRes;

    //read count of usb devices
    dwRes = RegQueryValueExW(hKey, _T("Count"), NULL, (LPDWORD) &type, (LPBYTE) &USBser_count, &size);
    if (dwRes) return 0;

    if (USBser_count)
    {
        for (INT i=0, dwRes = ERROR_SUCCESS; i<USBser_count; i++)
        {
            WCHAR achValue[MAX_VALUE_LENGTH];
            WCHAR buffer[MAX_VALUE_LENGTH];
            ZeroMemory(buffer, sizeof WCHAR  * MAX_VALUE_LENGTH);

            swprintf(achValue, L"%d",i); // read value name "0", "1"...
            dwRes = RegQueryValueExW(hKey, achValue, NULL, (LPDWORD) &type, (LPBYTE) &buffer, &size);

            // Plug that value into "SYSTEM\\CurrentControlSet\\Enum\\"
            HKEY hKey2;
            swprintf(achValue, L"SYSTEM\\CurrentControlSet\\Enum\\%s",buffer);

            INT dwRegOPenKey2 = RegOpenKeyExW(HKEY_LOCAL_MACHINE, achValue, 0, KEY_READ, &hKey2);
            if (dwRegOPenKey2) return 0; // check if this key exists

            // From here read friendly name
            dwRes = RegQueryValueExW(hKey2, _T("FriendlyName"), NULL, (LPDWORD) &type, (LPBYTE) &buffer, &size);
            if (dwRes) return 0;

            // or read COM port
            swprintf(achValue, L"%s\\Device Parameters", achValue);
            dwRegOPenKey2 = RegOpenKeyExW(HKEY_LOCAL_MACHINE, achValue, 0, KEY_READ, &hKey2);
            if (dwRegOPenKey2) return 0;

            dwRes = RegQueryValueExW(hKey2, _T("PortName"), NULL, (LPDWORD) &type, (LPBYTE) &buffer, &size);
            if (dwRes) return 0;
        }
    }
}