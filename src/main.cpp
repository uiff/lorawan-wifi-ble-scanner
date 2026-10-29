/**
 * IoTUeli.ch - 3-in-1 IoT Network Finder (LoRaWAN 868 MHz + WiFi 2.4 GHz + BLE)
 * Hardware: Heltec WiFi LoRa 32 V2 (ESP32 + SX1276 + 0.96" OLED SSD1306)
 *
 * EINFACHE 5-SEITEN-BEDIENUNG:
 *   - Taster LINKS  (‹) [GPIO 12] : Vorherige Seite (1/5 <-> 2/5 <-> 3/5 <-> 4/5 <-> 5/5)
 *   - Taster RECHTS (›) [GPIO 32] : Nächste Seite   (1/5 <-> 2/5 <-> 3/5 <-> 4/5 <-> 5/5)
 *   - Taster MITTE  (●) [GPIO 13] : Aktion auf der aktuellen Seite ausführen:
 *       * Seite 1 (1/5 LORA-CHECK)  : [NEU MESSEN] 3-Sekunden 868-MHz Messung starten
 *       * Seite 2 (2/5 LORA-NETZ)   : [RESET]      Gefundenes LoRaWAN-Netz zurücksetzen
 *       * Seite 3 (3/5 LORA-TEST)   : [SENDEN!]    Test-Signal an Dragino/Gateway senden
 *       * Seite 4 (4/5 WIFI-SCAN)   : [NAECHSTES]  Durch gefundene WLANs blättern / neu scannen
 *       * Seite 5 (5/5 BLE-SCAN)    : [NAECHSTES]  Durch Bluetooth-Geräte blättern / neu scannen
 */

#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <WiFi.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>
#include <SSD1306Wire.h>
#include <RadioLib.h>
#include "logo_iotueli.h"

// ============================================================================
// Pin-Definitionen Heltec WiFi LoRa 32 V2
// ============================================================================
#define PIN_OLED_SDA    4
#define PIN_OLED_SCL   15
#define PIN_OLED_RST   16
#define PIN_VEXT       21   // Aktiv LOW schaltet 3.3V für OLED

#define PIN_LORA_SCK    5
#define PIN_LORA_MISO  19
#define PIN_LORA_MOSI  27
#define PIN_LORA_NSS   18
#define PIN_LORA_RST   14
#define PIN_LORA_DIO0  26
#define PIN_LORA_DIO1  35

#define PIN_LED        25
#define PIN_BAT_ADC    37

#define PIN_BTN_LEFT   12
#define PIN_BTN_MID    13
#define PIN_BTN_RIGHT  32
#define PIN_BTN_PRG     0

// ============================================================================
// EU868 LoRaWAN Hauptkanäle (MHz) + Gateway-Downlink RX2 (869.525 MHz)
// ============================================================================
static const float EU868_MAIN_CHANNELS[4] = {
    868.1f, 868.3f, 868.5f, 869.525f
};

// ============================================================================
// Standard 5x7 Voll-ASCII Schriftart (ASCII 32..126)
// ============================================================================
static const uint8_t FONT5X7[95][5] PROGMEM = {
    {0x00, 0x00, 0x00, 0x00, 0x00}, // 32 ' '
    {0x00, 0x00, 0x5F, 0x00, 0x00}, // 33 '!'
    {0x00, 0x07, 0x00, 0x07, 0x00}, // 34 '"'
    {0x14, 0x7F, 0x14, 0x7F, 0x14}, // 35 '#'
    {0x24, 0x2A, 0x7F, 0x2A, 0x12}, // 36 '$'
    {0x23, 0x13, 0x08, 0x64, 0x62}, // 37 '%'
    {0x36, 0x49, 0x55, 0x22, 0x50}, // 38 '&'
    {0x00, 0x05, 0x03, 0x00, 0x00}, // 39 '''
    {0x00, 0x1C, 0x22, 0x41, 0x00}, // 40 '('
    {0x00, 0x41, 0x22, 0x1C, 0x00}, // 41 ')'
    {0x14, 0x08, 0x3E, 0x08, 0x14}, // 42 '*'
    {0x08, 0x08, 0x3E, 0x08, 0x08}, // 43 '+'
    {0x00, 0x50, 0x30, 0x00, 0x00}, // 44 ','
    {0x08, 0x08, 0x08, 0x08, 0x08}, // 45 '-'
    {0x00, 0x60, 0x60, 0x00, 0x00}, // 46 '.'
    {0x20, 0x10, 0x08, 0x04, 0x02}, // 47 '/'
    {0x3E, 0x51, 0x49, 0x45, 0x3E}, // 48 '0'
    {0x00, 0x42, 0x7F, 0x40, 0x00}, // 49 '1'
    {0x42, 0x61, 0x51, 0x49, 0x46}, // 50 '2'
    {0x21, 0x41, 0x45, 0x4B, 0x31}, // 51 '3'
    {0x18, 0x14, 0x12, 0x7F, 0x10}, // 52 '4'
    {0x27, 0x45, 0x45, 0x45, 0x39}, // 53 '5'
    {0x3C, 0x4A, 0x49, 0x49, 0x30}, // 54 '6'
    {0x01, 0x71, 0x09, 0x05, 0x03}, // 55 '7'
    {0x36, 0x49, 0x49, 0x49, 0x36}, // 56 '8'
    {0x06, 0x49, 0x49, 0x29, 0x1E}, // 57 '9'
    {0x00, 0x36, 0x36, 0x00, 0x00}, // 58 ':'
    {0x00, 0x56, 0x36, 0x00, 0x00}, // 59 ';'
    {0x08, 0x14, 0x22, 0x41, 0x00}, // 60 '<'
    {0x14, 0x14, 0x14, 0x14, 0x14}, // 61 '='
    {0x00, 0x41, 0x22, 0x14, 0x08}, // 62 '>'
    {0x02, 0x01, 0x51, 0x09, 0x06}, // 63 '?'
    {0x32, 0x49, 0x79, 0x41, 0x3E}, // 64 '@'
    {0x7E, 0x11, 0x11, 0x11, 0x7E}, // 65 'A'
    {0x7F, 0x49, 0x49, 0x49, 0x36}, // 66 'B'
    {0x3E, 0x41, 0x41, 0x41, 0x22}, // 67 'C'
    {0x7F, 0x41, 0x41, 0x22, 0x1C}, // 68 'D'
    {0x7F, 0x49, 0x49, 0x49, 0x41}, // 69 'E'
    {0x7F, 0x09, 0x09, 0x09, 0x01}, // 70 'F'
    {0x3E, 0x41, 0x49, 0x49, 0x7A}, // 71 'G'
    {0x7F, 0x08, 0x08, 0x08, 0x7F}, // 72 'H'
    {0x00, 0x41, 0x7F, 0x41, 0x00}, // 73 'I'
    {0x20, 0x40, 0x41, 0x3F, 0x01}, // 74 'J'
    {0x7F, 0x08, 0x14, 0x22, 0x41}, // 75 'K'
    {0x7F, 0x40, 0x40, 0x40, 0x40}, // 76 'L'
    {0x7F, 0x02, 0x0C, 0x02, 0x7F}, // 77 'M'
    {0x7F, 0x04, 0x08, 0x10, 0x7F}, // 78 'N'
    {0x3E, 0x41, 0x41, 0x41, 0x3E}, // 79 'O'
    {0x7F, 0x09, 0x09, 0x09, 0x06}, // 80 'P'
    {0x3E, 0x41, 0x51, 0x21, 0x5E}, // 81 'Q'
    {0x7F, 0x09, 0x19, 0x29, 0x46}, // 82 'R'
    {0x46, 0x49, 0x49, 0x49, 0x31}, // 83 'S'
    {0x01, 0x01, 0x7F, 0x01, 0x01}, // 84 'T'
    {0x3F, 0x40, 0x40, 0x40, 0x3F}, // 85 'U'
    {0x1F, 0x20, 0x40, 0x20, 0x1F}, // 86 'V'
    {0x3F, 0x40, 0x38, 0x40, 0x3F}, // 87 'W'
    {0x63, 0x14, 0x08, 0x14, 0x63}, // 88 'X'
    {0x07, 0x08, 0x70, 0x08, 0x07}, // 89 'Y'
    {0x61, 0x51, 0x49, 0x45, 0x43}, // 90 'Z'
    {0x00, 0x7F, 0x41, 0x41, 0x00}, // 91 '['
    {0x02, 0x04, 0x08, 0x10, 0x20}, // 92 '\'
    {0x00, 0x41, 0x41, 0x7F, 0x00}, // 93 ']'
    {0x04, 0x02, 0x01, 0x02, 0x04}, // 94 '^'
    {0x40, 0x40, 0x40, 0x40, 0x40}, // 95 '_'
    {0x00, 0x01, 0x02, 0x04, 0x00}, // 96 '`'
    {0x20, 0x54, 0x54, 0x54, 0x78}, // 97 'a'
    {0x7F, 0x48, 0x44, 0x44, 0x38}, // 98 'b'
    {0x38, 0x44, 0x44, 0x44, 0x20}, // 99 'c'
    {0x38, 0x44, 0x44, 0x48, 0x7F}, // 100 'd'
    {0x38, 0x54, 0x54, 0x54, 0x18}, // 101 'e'
    {0x08, 0x7E, 0x09, 0x01, 0x02}, // 102 'f'
    {0x0C, 0x52, 0x52, 0x52, 0x3E}, // 103 'g'
    {0x7F, 0x08, 0x04, 0x04, 0x78}, // 104 'h'
    {0x00, 0x44, 0x7D, 0x40, 0x00}, // 105 'i'
    {0x20, 0x40, 0x44, 0x3D, 0x00}, // 106 'j'
    {0x7F, 0x10, 0x28, 0x44, 0x00}, // 107 'k'
    {0x00, 0x41, 0x7F, 0x40, 0x00}, // 108 'l'
    {0x7C, 0x04, 0x18, 0x04, 0x78}, // 109 'm'
    {0x7C, 0x08, 0x04, 0x04, 0x78}, // 110 'n'
    {0x38, 0x44, 0x44, 0x44, 0x38}, // 111 'o'
    {0x7C, 0x14, 0x14, 0x14, 0x08}, // 112 'p'
    {0x08, 0x14, 0x14, 0x18, 0x7C}, // 113 'q'
    {0x7C, 0x08, 0x04, 0x04, 0x08}, // 114 'r'
    {0x48, 0x54, 0x54, 0x54, 0x20}, // 115 's'
    {0x04, 0x3F, 0x44, 0x40, 0x20}, // 116 't'
    {0x3C, 0x40, 0x40, 0x20, 0x7C}, // 117 'u'
    {0x1C, 0x20, 0x40, 0x20, 0x1C}, // 118 'v'
    {0x3C, 0x40, 0x30, 0x40, 0x3C}, // 119 'w'
    {0x44, 0x28, 0x10, 0x28, 0x44}, // 120 'x'
    {0x0C, 0x50, 0x50, 0x50, 0x3C}, // 121 'y'
    {0x44, 0x64, 0x54, 0x4C, 0x44}, // 122 'z'
    {0x00, 0x08, 0x36, 0x41, 0x00}, // 123 '{'
    {0x00, 0x00, 0x7F, 0x00, 0x00}, // 124 '|'
    {0x00, 0x41, 0x36, 0x08, 0x00}, // 125 '}'
    {0x08, 0x04, 0x08, 0x10, 0x08}  // 126 '~'
};

// ============================================================================
// Globale Objekte (Display & SX1276 Radio)
// ============================================================================
SSD1306Wire display(0x3c, PIN_OLED_SDA, PIN_OLED_SCL, GEOMETRY_128_64);
SPIClass loraSPI(VSPI);
SX1276 radio = new Module(PIN_LORA_NSS, PIN_LORA_DIO0, PIN_LORA_RST, PIN_LORA_DIO1, loraSPI);

// ============================================================================
// 128x32 Scanline-Safe Zeichenfunktionen (ly = 0..31 -> physisch y = 2*ly, 2*ly+1)
// ============================================================================
static inline void lSetPixel(int16_t x, int16_t ly) {
    if (x < 0 || x >= 128 || ly < 0 || ly >= 32) return;
    display.setPixel(x, ly * 2);
    display.setPixel(x, ly * 2 + 1);
}

static void lDrawHLine(int16_t x, int16_t ly, int16_t w) {
    for (int16_t i = 0; i < w; i++) lSetPixel(x + i, ly);
}

static void lDrawVLine(int16_t x, int16_t ly, int16_t h) {
    for (int16_t j = 0; j < h; j++) lSetPixel(x, ly + j);
}

static void lDrawRect(int16_t x, int16_t ly, int16_t w, int16_t h) {
    lDrawHLine(x, ly, w);
    lDrawHLine(x, ly + h - 1, w);
    lDrawVLine(x, ly, h);
    lDrawVLine(x + w - 1, ly, h);
}

static void lFillRect(int16_t x, int16_t ly, int16_t w, int16_t h) {
    for (int16_t j = 0; j < h; j++) lDrawHLine(x, ly + j, w);
}

static int16_t lDrawChar(int16_t x, int16_t ly, char c, uint8_t scaleX = 1) {
    if (c < 32 || c > 126) c = '?';
    uint8_t idx = (uint8_t)(c - 32);
    for (uint8_t col = 0; col < 5; col++) {
        uint8_t bits = pgm_read_byte(&FONT5X7[idx][col]);
        for (uint8_t row = 0; row < 7; row++) {
            if (bits & (1 << row)) {
                for (uint8_t sx = 0; sx < scaleX; sx++) {
                    lSetPixel(x + col * scaleX + sx, ly + row);
                }
            }
        }
    }
    return 5 * scaleX + scaleX;
}

static void lDrawStr(int16_t x, int16_t ly, const char* str) {
    int16_t curX = x;
    while (*str) curX += lDrawChar(curX, ly, *str++, 1);
}

static void lDrawStrCentered(int16_t ly, const char* str) {
    int16_t len = (int16_t)strlen(str);
    int16_t w = len * 6 - 1;
    int16_t x = (128 - w) / 2;
    if (x < 0) x = 0;
    lDrawStr(x, ly, str);
}

static void lDrawStrWide(int16_t x, int16_t ly, const char* str) {
    int16_t curX = x;
    while (*str) curX += lDrawChar(curX, ly, *str++, 2);
}

static void lDrawStrWideCentered(int16_t ly, const char* str) {
    int16_t len = (int16_t)strlen(str);
    int16_t w = len * 12 - 2;
    int16_t x = (128 - w) / 2;
    if (x < 0) x = 0;
    lDrawStrWide(x, ly, str);
}

// ============================================================================
// Einfache Signal-Umrechnung in Prozent (0..100%) und Klartext-Urteil
// Spreizung -115 dBm (0%) bis -35 dBm (100%), damit 1m vs. 10m klar sichtbar ist!
// ============================================================================
int rssiToPercent(float rssi) {
    if (rssi < -115.0f) return 0;
    int pct = (int)((rssi + 115.0f) * 100.0f / 80.0f); // -115 dBm = 0%, -35 dBm = 100%
    if (pct < 5) pct = 5;
    if (pct > 100) pct = 100;
    return pct;
}

const char* rssiToVerdict(float rssi) {
    if (rssi >= -75.0f)  return "SEHR GUT!";
    if (rssi >= -100.0f) return "GUT (OK)";
    if (rssi >= -115.0f) return "SCHWACH";
    return "KEIN SIGNAL";
}

// Für WLAN / BLE (2.4 GHz hat höhere Pegel: -30..-90 dBm)
const char* wifiBleVerdict(int rssi) {
    if (rssi >= -67) return "SEHR GUT!";
    if (rssi >= -78) return "GUT (OK)";
    if (rssi >= -88) return "SCHWACH";
    return "SEHR SCHWACH";
}

int wifiBlePercent(int rssi) {
    int pct = (rssi + 95) * 100 / 55; // -95 dBm = 0%, -40 dBm = 100%
    if (pct < 5) pct = 5;
    if (pct > 100) pct = 100;
    return pct;
}

// ============================================================================
// LoRaWAN-Netzbetreiber + kurze Kennung (DevAddr/DevEUI) erkennen,
// damit MEHRERE LoRaWAN-Netze & Sensoren unterschieden werden können!
// ============================================================================
String identifyLoRaWanNetwork(const uint8_t* data, int len) {
    char idBuf[20];
    if (len < 4) return "LORA FUNK";
    uint8_t mtype = (data[0] >> 5) & 0x07;

    // 1. Join-Request (23 Bytes): DevEUI in Bytes 9..16 (Little Endian)
    if (mtype == 0 && len >= 17) {
        uint8_t oui0 = data[16];
        uint8_t oui1 = data[15];
        uint8_t devLo = data[9];
        if (oui0 == 0xA8 && oui1 == 0x40) {
            snprintf(idBuf, sizeof(idBuf), "DRAGINO #%02X", devLo);
            return String(idBuf);
        }
        snprintf(idBuf, sizeof(idBuf), "JOIN #%02X%02X", oui0, devLo);
        return String(idBuf);
    }

    // 2. Join-Accept vom Gateway
    if (mtype == 1) {
        return "GW JOIN-OK";
    }

    // 3. Daten-Paket (Uplink / Downlink): DevAddr in Bytes 1..4 (Little Endian, MSB = data[4])
    if (len >= 8 && (mtype >= 2 && mtype <= 5)) {
        uint8_t msb = data[4];
        uint8_t b2  = data[3];
        uint8_t lsb = data[1];
        const char* net = "LORA";
        if (msb == 0x06 || msb == 0x07 || msb == 0x5A || msb == 0x5B) net = "SWISSCOM";
        else if (msb == 0x26 || msb == 0x27)                          net = "TTN/DRAG";
        else if (msb == 0x48 || msb == 0x49)                          net = "HELIUM";
        else if ((msb >= 0x18 && msb <= 0x1F) || msb == 0x30 || msb == 0x31) net = "LORIOT";
        else if (msb <= 0x03 || msb >= 0xFC)                          net = "PRIVAT";

        snprintf(idBuf, sizeof(idBuf), "%s %02X%02X", net, b2, lsb);
        return String(idBuf);
    }

    snprintf(idBuf, sizeof(idBuf), "LORA #%02X%02X", data[0], data[1]);
    return String(idBuf);
}

// ============================================================================
// 5 Übersichts-Seiten (Blättern einfach mit LINKS < und RECHTS >)
// ============================================================================
enum ScreenPage : uint8_t {
    PAGE_SIGNAL_CHECK = 0,  // Seite 1/5: LoRa 868 MHz Signal-Check (echte Pakete, dBm + %)
    PAGE_NET_FINDER   = 1,  // Seite 2/5: Alle gefundenen LoRaWAN-Netze durchblättern
    PAGE_SEND_TEST    = 2,  // Seite 3/5: LoRaWAN Sende-Test an Dragino/Gateway
    PAGE_WIFI_SCAN    = 3,  // Seite 4/5: 2.4 GHz WLAN-Scanner (SSID + Bewertung)
    PAGE_BLE_SCAN     = 4,  // Seite 5/5: Bluetooth BLE-Scanner (Name/MAC + Bewertung)
    PAGE_COUNT        = 5
};

static ScreenPage currentPage = PAGE_SIGNAL_CHECK;
static bool loraReady = false;
static volatile bool rxFlag = false;

// --- LoRaWAN Multi-Netzwerk-Liste (bis zu 10 Netze/Sender auf Seite 2/5) ---
struct LoraEntry {
    String name;      // z.B. "SWISSCOM 12A4" oder "TTN/DRAG 01FE"
    float rssi;       // Letzter echter Paket-RSSI in dBm
    float snr;        // Letzter Paket-SNR in dB
    float freqMHz;    // Empfangsfrequenz (z.B. 868.1 MHz)
    uint32_t seenMs;  // Zeitpunkt des letzten Empfangs
    uint16_t count;   // Anzahl empfangener Pakete dieses Senders
};
static LoraEntry loraList[10];
static int loraCount = 0;
static int loraSelectedIdx = 0;

// --- LoRaWAN Aktuellster Messwert für Seite 1/5 ---
static float lastPacketRssi = -125.0f;
static uint32_t lastPacketMs = 0;
static uint32_t packetCount = 0;
static uint32_t sendTestCount = 0;
static String sendTestResult = "Mitte = Senden";
static uint8_t hopIdx = 0;
static bool listenGatewayIQ = false;

// --- WiFi-Scanner Zustand (Seite 4/5) ---
struct WifiEntry {
    String ssid;
    int rssi;
};
static WifiEntry wifiList[8];
static int wifiCount = 0;
static int wifiSelectedIdx = 0;
static bool wifiScannedOnce = false;

// --- BLE-Scanner Zustand (Seite 5/5) ---
struct BleEntry {
    String name;
    int rssi;
};
static BleEntry bleList[8];
static int bleCount = 0;
static int bleSelectedIdx = 0;
static bool bleScannedOnce = false;
static bool bleInitialized = false;

// ============================================================================
// Interrupt-Routine für Paket-Empfang (DIO0)
// ============================================================================
#if defined(ESP8266) || defined(ESP32)
ICACHE_RAM_ATTR
#endif
void onDio0Rise() {
    rxFlag = true;
}

// ============================================================================
// Einfache Taster-Abfrage
// ============================================================================
struct SimpleButton {
    uint8_t pin;
    bool lastLevel;
    uint32_t lastChangeMs;
};

static SimpleButton btnLeft  = {PIN_BTN_LEFT,  HIGH, 0};
static SimpleButton btnMid   = {PIN_BTN_MID,   HIGH, 0};
static SimpleButton btnRight = {PIN_BTN_RIGHT, HIGH, 0};
static SimpleButton btnPrg   = {PIN_BTN_PRG,   HIGH, 0};

bool wasButtonPressed(SimpleButton &b) {
    bool level = digitalRead(b.pin);
    uint32_t now = millis();
    if (level != b.lastLevel && (now - b.lastChangeMs > 40)) {
        b.lastChangeMs = now;
        b.lastLevel = level;
        if (level == LOW) return true;
    }
    return false;
}

// ============================================================================
// Akku-Spannung auslesen
// ============================================================================
int readBatteryPercent() {
    uint16_t raw = analogRead(PIN_BAT_ADC);
    float vbat = (raw / 4095.0f) * 3.3f * 3.2f;
    if (vbat < 3.0f) return 100;
    int pct = (int)((vbat - 3.3f) / (4.15f - 3.3f) * 100.0f);
    if (pct < 0) pct = 0;
    if (pct > 100) pct = 100;
    return pct;
}

// ============================================================================
// Funkmodul einstellen
// ============================================================================
void configureRadio(float freqMHz, uint8_t sf, bool gatewayDownlinkIQ) {
    if (!loraReady) return;
    radio.standby();
    radio.setFrequency(freqMHz);
    radio.setBandwidth(125.0f);
    radio.setSpreadingFactor(sf);
    radio.setCodingRate(5);
    radio.setSyncWord(0x34);
    radio.setPreambleLength(8);
    radio.setCRC(!gatewayDownlinkIQ);
    radio.invertIQ(gatewayDownlinkIQ);

    rxFlag = false;
    radio.setDio0Action(onDio0Rise, RISING);
    radio.startReceive();
}

// ============================================================================
// Kopfzeile (ly = 0..6) + Trennlinie (ly = 7)
// ============================================================================
void drawHeader(const char* title) {
    lDrawStr(0, 0, title);

    int pct = readBatteryPercent();
    lDrawRect(112, 0, 14, 7);
    lFillRect(126, 2, 2, 3);
    int fillW = (pct * 10) / 100;
    if (fillW > 0) lFillRect(114, 2, fillW, 3);

    lDrawHLine(0, 7, 128);
}

// ============================================================================
// Boot-Screen mit IoTUeli.ch Logo
// ============================================================================
void showBootLogo() {
    display.clear();
    int16_t logoX = (128 - IOTUELI_LOGO_WIDTH) / 2;
    display.drawXbm(logoX, 0, IOTUELI_LOGO_WIDTH, IOTUELI_LOGO_HEIGHT, IOTUELI_LOGO_XBM);
    lDrawStrCentered(24, "iotueli.ch Finder");
    display.display();

    digitalWrite(PIN_LED, HIGH);
    delay(2500);
    digitalWrite(PIN_LED, LOW);
}

// ============================================================================
// Gefundenes LoRaWAN-Netz / Sender in die Multi-Netz-Liste eintragen
// ============================================================================
static float currentFreqMHz = 868.1f;

void recordLoRaPacket(const String& netName, float rssi, float snr, float freqMHz) {
    lastPacketRssi = rssi;
    lastPacketMs = millis();
    packetCount++;

    // Prüfen, ob dieser Sender/Netzname schon in der Liste (bis 10 Einträge) existiert
    for (int i = 0; i < loraCount; i++) {
        if (loraList[i].name == netName) {
            loraList[i].rssi = rssi;      // Aktuellen Live-RSSI speichern (nicht einfrieren!)
            loraList[i].snr = snr;
            loraList[i].freqMHz = freqMHz;
            loraList[i].seenMs = lastPacketMs;
            loraList[i].count++;
            loraSelectedIdx = i;
            return;
        }
    }

    // Neuer Eintrag (oder ältesten ersetzen, falls 10 voll)
    int idx = loraCount;
    if (idx >= 10) {
        idx = 0;
        uint32_t oldest = loraList[0].seenMs;
        for (int i = 1; i < 10; i++) {
            if (loraList[i].seenMs < oldest) {
                oldest = loraList[i].seenMs;
                idx = i;
            }
        }
    } else {
        loraCount++;
    }

    loraList[idx].name = netName;
    loraList[idx].rssi = rssi;
    loraList[idx].snr = snr;
    loraList[idx].freqMHz = freqMHz;
    loraList[idx].seenMs = lastPacketMs;
    loraList[idx].count = 1;
    loraSelectedIdx = idx;
}

// ============================================================================
// Hintergrund-Überwachung für LoRa 868 MHz (läuft auf Seiten 1..3)
// WICHTIG: Kein ungefiltertes getRSSI(false) mehr (verhinderte den 38% / -94 dBm
// Grundrauschen-Spike!). Nur echte LoRa-Pakete werden gewertet!
// ============================================================================
void backgroundMonitorLoRa() {
    static uint32_t lastHopMs = 0;
    if (!loraReady) return;

    if (rxFlag) {
        rxFlag = false;
        int len = radio.getPacketLength();
        if (len <= 0 || len > 255) len = 64;
        uint8_t data[256];
        int state = radio.readData(data, len);

        if ((state == RADIOLIB_ERR_NONE || state == RADIOLIB_ERR_CRC_MISMATCH) && len >= 4) {
            digitalWrite(PIN_LED, HIGH);
            float rssi = radio.getRSSI(); // Echter Paket-RSSI des LoRa-Modems!
            float snr  = radio.getSNR();
            String netName = identifyLoRaWanNetwork(data, len);
            recordLoRaPacket(netName, rssi, snr, currentFreqMHz);
            delay(15);
            digitalWrite(PIN_LED, LOW);
        }
        radio.startReceive();
    }

    if (millis() - lastHopMs > 450) {
        lastHopMs = millis();
        hopIdx = (hopIdx + 1) & 0x07;
        currentFreqMHz = EU868_MAIN_CHANNELS[hopIdx & 0x03];
        listenGatewayIQ = (hopIdx >= 4);
        uint8_t sf = (currentFreqMHz > 869.0f) ? 9 : 7;
        configureRadio(currentFreqMHz, sf, listenGatewayIQ);
    }
}

// ============================================================================
// Seite 1 Aktion: 3-Sekunden LoRa Intensiv-Messung
// Horcht auf echte LoRaWAN-Pakete über alle Hauptkanäle (ohne 38%-Rausch-Bug!)
// ============================================================================
void runIntensiveSignalCheck() {
    if (!loraReady) return;
    lastPacketRssi = -125.0f;
    lastPacketMs = 0;

    static const float ALL_CH[4] = { 868.1f, 868.3f, 868.5f, 869.525f };

    uint32_t startMs = millis();
    int chIdx = 0;
    currentFreqMHz = ALL_CH[0];
    configureRadio(currentFreqMHz, 7, false);
    uint32_t lastSwitchMs = startMs;

    while (millis() - startMs < 3000) {
        uint32_t now = millis();
        uint32_t elapsed = now - startMs;
        int progressW = (int)(elapsed * 124 / 3000);

        if (rxFlag) {
            rxFlag = false;
            int len = radio.getPacketLength();
            if (len <= 0 || len > 255) len = 64;
            uint8_t data[256];
            int state = radio.readData(data, len);
            if ((state == RADIOLIB_ERR_NONE || state == RADIOLIB_ERR_CRC_MISMATCH) && len >= 4) {
                digitalWrite(PIN_LED, HIGH);
                float rssi = radio.getRSSI();
                float snr  = radio.getSNR();
                String netName = identifyLoRaWanNetwork(data, len);
                recordLoRaPacket(netName, rssi, snr, currentFreqMHz);
                digitalWrite(PIN_LED, LOW);
            }
            radio.startReceive();
        }

        // Alle 180 ms Kanal / IQ wechseln (damit ein komplettes SF7/SF9 Paket reinpasst)
        if (now - lastSwitchMs > 180) {
            lastSwitchMs = now;
            chIdx = (chIdx + 1) & 0x07;
            currentFreqMHz = ALL_CH[chIdx & 0x03];
            bool gwIQ = (chIdx >= 4);
            uint8_t sf = (currentFreqMHz > 869.0f) ? 9 : 7;
            configureRadio(currentFreqMHz, sf, gwIQ);
        }

        display.clear();
        drawHeader("1/5 LORA-CHECK");
        lDrawStrCentered(10, "HORCHE 868 MHz...");
        lDrawRect(0, 19, 128, 7);
        if (progressW > 0) lFillRect(2, 21, progressW, 3);
        display.display();
        delay(10);
    }

    currentFreqMHz = 868.1f;
    configureRadio(868.1f, 7, false);
}

// ============================================================================
// Seite 3 Aktion: LoRaWAN Sende-Test (868.1, 868.3, 868.5 MHz)
// ============================================================================
void runSendTest() {
    if (!loraReady) {
        sendTestResult = "Funk-Fehler!";
        return;
    }

    sendTestCount++;
    bool gotReply = false;

    for (int i = 0; i < 3; i++) {
        float txFreq = EU868_MAIN_CHANNELS[i];
        currentFreqMHz = txFreq;
        char buf[26];
        display.clear();
        drawHeader("3/5 GATEWAY-TEST");
        lDrawStrWideCentered(10, "SENDE...");
        snprintf(buf, sizeof(buf), "Kanal %.1f MHz", txFreq);
        lDrawStrCentered(22, buf);
        display.display();

        digitalWrite(PIN_LED, HIGH);
        configureRadio(txFreq, 7, false);
        radio.clearDio0Action();

        uint8_t pkt[16] = {
            0x40, 0xFE, 0xCA, 0x01, 0x26, 0x80,
            (uint8_t)(sendTestCount & 0xFF), (uint8_t)((sendTestCount >> 8) & 0xFF),
            0x01, 'I', 'O', 'T', 'U', 'E', 'L', 'I'
        };
        radio.transmit(pkt, sizeof(pkt));
        digitalWrite(PIN_LED, LOW);

        // Nach dem Senden 1.1s lang im Gateway-Downlink-Modus (RX1 / RX2) horchen
        configureRadio(txFreq, 7, true);
        uint32_t t0 = millis();
        while (millis() - t0 < 1100) {
            if (rxFlag) {
                rxFlag = false;
                uint8_t rxBuf[128];
                int len = radio.getPacketLength();
                if (len <= 0 || len > 128) len = 64;
                int st = radio.readData(rxBuf, len);
                if (st == RADIOLIB_ERR_NONE || st == RADIOLIB_ERR_CRC_MISMATCH) {
                    gotReply = true;
                    float rssi = radio.getRSSI();
                    float snr  = radio.getSNR();
                    String netName = identifyLoRaWanNetwork(rxBuf, len);
                    recordLoRaPacket(netName, rssi, snr, txFreq);
                    break;
                }
            }
            delay(5);
        }
        if (gotReply) break;
    }

    if (gotReply) {
        char buf[26];
        snprintf(buf, sizeof(buf), "GW OK: %ddBm (%d%%)", (int)lastPacketRssi, rssiToPercent(lastPacketRssi));
        sendTestResult = String(buf);
    } else {
        char buf[26];
        snprintf(buf, sizeof(buf), "Gesendet (#%lu) OK!", (unsigned long)sendTestCount);
        sendTestResult = String(buf);
    }

    currentFreqMHz = 868.1f;
    configureRadio(868.1f, 7, false);
}

// ============================================================================
// Seite 4 Aktion: 2.4 GHz WiFi-Scanner
// ============================================================================
void runWifiScan() {
    display.clear();
    drawHeader("4/5 WIFI-SCAN");
    lDrawStrCentered(11, "SUCHE WLAN...");
    lDrawStrCentered(20, "2.4 GHz Band");
    display.display();

    digitalWrite(PIN_LED, HIGH);
    WiFi.mode(WIFI_STA);
    WiFi.disconnect();
    delay(50);

    int n = WiFi.scanNetworks(false, false, false, 200);
    wifiCount = 0;
    wifiSelectedIdx = 0;

    if (n > 0) {
        for (int i = 0; i < n && wifiCount < 8; i++) {
            String s = WiFi.SSID(i);
            if (s.length() == 0) s = "(Versteckt)";
            if (s.length() > 16) s = s.substring(0, 16);
            wifiList[wifiCount].ssid = s;
            wifiList[wifiCount].rssi = WiFi.RSSI(i);
            wifiCount++;
        }
    }
    WiFi.scanDelete();
    WiFi.mode(WIFI_OFF);
    digitalWrite(PIN_LED, LOW);
    wifiScannedOnce = true;
}

// ============================================================================
// Seite 5 Aktion: Bluetooth BLE-Scanner
// ============================================================================
void runBleScan() {
    display.clear();
    drawHeader("5/5 BLE-SCAN");
    lDrawStrCentered(11, "SUCHE BLUETOOTH..");
    lDrawStrCentered(20, "BLE 2.4 GHz (2s)");
    display.display();

    digitalWrite(PIN_LED, HIGH);
    WiFi.mode(WIFI_OFF);

    if (!bleInitialized) {
        BLEDevice::init("");
        bleInitialized = true;
    }

    BLEScan* pBLEScan = BLEDevice::getScan();
    pBLEScan->setActiveScan(true);
    pBLEScan->setInterval(100);
    pBLEScan->setWindow(80);

    BLEScanResults* foundDevices = pBLEScan->start(2, false);
    int n = foundDevices ? foundDevices->getCount() : 0;
    bleCount = 0;
    bleSelectedIdx = 0;

    // Nach Signalstärke sortiert die besten 8 BLE-Geräte übernehmen
    for (int i = 0; i < n && bleCount < 8; i++) {
        BLEAdvertisedDevice dev = foundDevices->getDevice(i);
        String devName = dev.haveName() ? String(dev.getName().c_str()) : "";
        devName.trim();
        if (devName.length() == 0) {
            // MAC-Adresse anzeigen, falls kein Name gesendet wird
            String mac = String(dev.getAddress().toString().c_str());
            mac.toUpperCase();
            if (mac.length() >= 8) {
                devName = "BLE " + mac.substring(mac.length() - 8);
            } else {
                devName = "BLE Geraet";
            }
        }
        if (devName.length() > 16) devName = devName.substring(0, 16);
        bleList[bleCount].name = devName;
        bleList[bleCount].rssi = dev.getRSSI();
        bleCount++;
    }

    pBLEScan->clearResults();
    digitalWrite(PIN_LED, LOW);
    bleScannedOnce = true;
}

// ============================================================================
// Zeichenfunktionen für alle 5 Seiten
// ============================================================================
void drawPageSignalCheck() {
    drawHeader("1/5 LORA-CHECK");

    int pct = (lastPacketMs == 0) ? 0 : rssiToPercent(lastPacketRssi);
    char buf[26];

    if (pct == 0) {
        lDrawStrCentered(9, "RUHE (Kein Paket)");
        lDrawStrCentered(17, "Warte auf 868MHz..");
    } else {
        uint32_t ageSec = (millis() - lastPacketMs) / 1000;
        snprintf(buf, sizeof(buf), "%s %d%%", rssiToVerdict(lastPacketRssi), pct);
        lDrawStrCentered(9, buf);

        if (ageSec < 999) {
            snprintf(buf, sizeof(buf), "%ddBm (vor %lus)", (int)lastPacketRssi, (unsigned long)ageSec);
        } else {
            snprintf(buf, sizeof(buf), "%ddBm (#%lu)", (int)lastPacketRssi, (unsigned long)packetCount);
        }
        lDrawStrCentered(17, buf);
    }

    lDrawStr(0, 25, "<   [NEU MESSEN]    >");
}

void drawPageNetFinder() {
    char buf[26];
    snprintf(buf, sizeof(buf), "2/5 LORA (%d)", loraCount);
    drawHeader(buf);

    if (loraCount == 0) {
        lDrawStrCentered(9, "Kein LoRa empf.");
        lDrawStrCentered(17, "Horche 868 MHz...");
        lDrawStr(0, 25, "<   [NEU MESSEN]    >");
    } else {
        if (loraSelectedIdx >= loraCount) loraSelectedIdx = 0;
        LoraEntry &e = loraList[loraSelectedIdx];

        snprintf(buf, sizeof(buf), "%d:%s", loraSelectedIdx + 1, e.name.c_str());
        lDrawStr(0, 9, buf);

        snprintf(buf, sizeof(buf), "%s %ddBm %d%%", rssiToVerdict(e.rssi), (int)e.rssi, rssiToPercent(e.rssi));
        lDrawStr(0, 17, buf);

        if (loraSelectedIdx + 1 < loraCount) {
            lDrawStr(0, 25, "<  [NAECHSTES LORA] >");
        } else {
            lDrawStr(0, 25, "<  [LISTE LEEREN]   >");
        }
    }
}

void drawPageSendTest() {
    drawHeader("3/5 LORA-TEST");

    lDrawStrCentered(9, sendTestResult.c_str());
    lDrawStrCentered(17, "Funk an Dragino/GW");

    lDrawStr(0, 25, "<    [SENDEN!]      >");
}

void drawPageWifiScan() {
    char buf[26];
    snprintf(buf, sizeof(buf), "4/5 WIFI (%d)", wifiCount);
    drawHeader(buf);

    if (wifiCount == 0) {
        lDrawStrCentered(9, "Kein WLAN gefunden");
        lDrawStrCentered(17, "Mitte = Neu suchen");
        lDrawStr(0, 25, "<   [NEU SUCHEN]    >");
    } else {
        WifiEntry &w = wifiList[wifiSelectedIdx];
        snprintf(buf, sizeof(buf), "%d:%s", wifiSelectedIdx + 1, w.ssid.c_str());
        lDrawStr(0, 9, buf);

        snprintf(buf, sizeof(buf), "%s (%d%%)", wifiBleVerdict(w.rssi), wifiBlePercent(w.rssi));
        lDrawStr(0, 17, buf);

        if (wifiSelectedIdx + 1 < wifiCount) {
            lDrawStr(0, 25, "<  [NAECHSTES WLAN] >");
        } else {
            lDrawStr(0, 25, "<   [NEU SUCHEN]    >");
        }
    }
}

void drawPageBleScan() {
    char buf[26];
    snprintf(buf, sizeof(buf), "5/5 BLE (%d)", bleCount);
    drawHeader(buf);

    if (bleCount == 0) {
        lDrawStrCentered(9, "Kein BLE gefunden");
        lDrawStrCentered(17, "Mitte = Neu suchen");
        lDrawStr(0, 25, "<   [NEU SUCHEN]    >");
    } else {
        BleEntry &b = bleList[bleSelectedIdx];
        snprintf(buf, sizeof(buf), "%d:%s", bleSelectedIdx + 1, b.name.c_str());
        lDrawStr(0, 9, buf);

        snprintf(buf, sizeof(buf), "%s (%d%%)", wifiBleVerdict(b.rssi), wifiBlePercent(b.rssi));
        lDrawStr(0, 17, buf);

        if (bleSelectedIdx + 1 < bleCount) {
            lDrawStr(0, 25, "<  [NAECHSTES BLE]  >");
        } else {
            lDrawStr(0, 25, "<   [NEU SUCHEN]    >");
        }
    }
}

// ============================================================================
// Beim Seitenwechsel ggf. ersten Scan auslösen
// ============================================================================
void onEnterPage(ScreenPage page) {
    if (page == PAGE_WIFI_SCAN && !wifiScannedOnce) {
        runWifiScan();
    } else if (page == PAGE_BLE_SCAN && !bleScannedOnce) {
        runBleScan();
    } else if (page <= PAGE_SEND_TEST) {
        configureRadio(868.1f, 7, false);
    }
}

// ============================================================================
// Setup & Loop
// ============================================================================
void setup() {
    Serial.begin(115200);

    pinMode(PIN_VEXT, OUTPUT);
    digitalWrite(PIN_VEXT, LOW);
    pinMode(PIN_LED, OUTPUT);
    digitalWrite(PIN_LED, LOW);

    pinMode(PIN_BTN_LEFT,  INPUT_PULLUP);
    pinMode(PIN_BTN_MID,   INPUT_PULLUP);
    pinMode(PIN_BTN_RIGHT, INPUT_PULLUP);
    pinMode(PIN_BTN_PRG,   INPUT_PULLUP);

    pinMode(PIN_OLED_RST, OUTPUT);
    digitalWrite(PIN_OLED_RST, LOW);
    delay(50);
    digitalWrite(PIN_OLED_RST, HIGH);
    delay(50);

    display.init();
    display.flipScreenVertically();

    showBootLogo();

    loraSPI.begin(PIN_LORA_SCK, PIN_LORA_MISO, PIN_LORA_MOSI, PIN_LORA_NSS);
    int state = radio.begin(868.1f, 125.0f, 7, 5, 0x34, 14, 8, 0);
    if (state == RADIOLIB_ERR_NONE) {
        loraReady = true;
        configureRadio(868.1f, 7, false);
    } else {
        loraReady = false;
    }
}

void loop() {
    if (wasButtonPressed(btnLeft)) {
        currentPage = (ScreenPage)((currentPage + PAGE_COUNT - 1) % PAGE_COUNT);
        onEnterPage(currentPage);
    }
    if (wasButtonPressed(btnRight) || wasButtonPressed(btnPrg)) {
        currentPage = (ScreenPage)((currentPage + 1) % PAGE_COUNT);
        onEnterPage(currentPage);
    }
    if (wasButtonPressed(btnMid)) {
        if (currentPage == PAGE_SIGNAL_CHECK) {
            runIntensiveSignalCheck();
        } else if (currentPage == PAGE_NET_FINDER) {
            if (loraCount == 0) {
                runIntensiveSignalCheck();
            } else if (loraSelectedIdx + 1 < loraCount) {
                loraSelectedIdx++;
            } else {
                // Am Ende der Liste: Liste zurücksetzen und neu horchen
                loraCount = 0;
                loraSelectedIdx = 0;
                packetCount = 0;
                lastPacketMs = 0;
                lastPacketRssi = -125.0f;
            }
        } else if (currentPage == PAGE_SEND_TEST) {
            runSendTest();
        } else if (currentPage == PAGE_WIFI_SCAN) {
            if (wifiCount > 0 && wifiSelectedIdx + 1 < wifiCount) {
                wifiSelectedIdx++;
            } else {
                runWifiScan();
            }
        } else if (currentPage == PAGE_BLE_SCAN) {
            if (bleCount > 0 && bleSelectedIdx + 1 < bleCount) {
                bleSelectedIdx++;
            } else {
                runBleScan();
            }
        }
    }

    // Auf den Seiten 1..3 läuft der 868-MHz LoRa-Detektor im Hintergrund
    if (currentPage <= PAGE_SEND_TEST) {
        backgroundMonitorLoRa();
    }

    static uint32_t lastDrawMs = 0;
    if (millis() - lastDrawMs > 65) {
        lastDrawMs = millis();
        display.clear();
        switch (currentPage) {
            case PAGE_SIGNAL_CHECK: drawPageSignalCheck(); break;
            case PAGE_NET_FINDER:   drawPageNetFinder();   break;
            case PAGE_SEND_TEST:    drawPageSendTest();    break;
            case PAGE_WIFI_SCAN:    drawPageWifiScan();    break;
            case PAGE_BLE_SCAN:     drawPageBleScan();     break;
            default: break;
        }
        display.display();
    }
}
