#!/usr/bin/env python3

import sys
import subprocess
import os
import re
import csv
from datetime import datetime

def install_pyserial():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyserial"])

try:
    import serial
except ImportError:
    print("pyserial not found. Installing...")
    install_pyserial()
    import serial

def change_port_permissions(port):
    try:
        subprocess.run(['sudo', 'chmod', 'a+rw', port], check=True)
        print(f"Changed permissions for {port}")
        return True
    except subprocess.CalledProcessError:
        print(f"Failed to change permissions for {port}")
        return False

def extract_nrds_values(port='/dev/ttyUSB4', baudrate=115200):
    try:
        # Try to open serial connection
        try:
            ser = serial.Serial(port, baudrate, timeout=1)
        except PermissionError:
            print(f"Permission denied for {port}. Attempting to change permissions...")
            if change_port_permissions(port):
                ser = serial.Serial(port, baudrate, timeout=1)
            else:
                print("Please run the script with sudo privileges.")
                sys.exit(1)

        # Send AT#NRDS command
        print("Sending AT#NRDS command...")
        ser.write(b'AT#NRDS\r\n')

        # Read response
        response = ''
        print("Reading the response...")
        while True:
            line = ser.readline().decode('utf-8').strip()
            response += line + '\n'
            if 'OK' in line or 'ERROR' in line:
                break

        # Close serial connection
        ser.close()
        print("Closing the connection...")

        # Debug: print raw response
#        print("Raw response:", response)

        # Extract values using regex
        pattern = r'#NRDS: (\d+)/(-?\d+),(\d+),(\d+),(\d+),(-?\d+),(-?\d+),(-?\d+),(\d+),(\d+),(\d+),(\d+)/(\d+),(\d+)/(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(-?\d+),(-?\d+),(\d+),(0[xX][0-9a-fA-F]+|[-+]?\d+),(-?\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(-?\d+),(-?\d+),(\d+)/(\d+)'

        match = re.search(pattern, response)

        if match:
            nrds_values = {
                'BAND': int(match.group(1)),
                'BW': int(match.group(2)),
                'SCG_STATE': int(match.group(3)),
                'NR-ARFCN': int(match.group(4)),
                'NR-PCI': int(match.group(5)),
                'RSRP': int(match.group(6)),
                'RSRQ': int(match.group(7)),
		'RSSI': int(match.group(8)),
                'CQI': int(match.group(9)),
                'RI': int(match.group(10)),
                'NR-RB': int(match.group(11)),
		'NR-DL-MCS': int(match.group(12)),
		'NR-UL-MCS': int(match.group(13)),
		'NR-DL-MOD': int(match.group(14)),
		'NR-UL-MOD': int(match.group(15)),
		'NR-BLER': int(match.group(16)),
		'UpLayerInd': int(match.group(17)),
		'RestrictDCNR': int(match.group(18)),
		'ENDC_Status': int(match.group(19)),
		'SCG_FailCause': int(match.group(20)),
		'NR-CHBW': int(match.group(21)),
		'BWP': int(match.group(22)),
		'NR-SRB3': int(match.group(23)),
		'NR-SSB': int(match.group(24)),
		'NR-SSB-RSRP': int(match.group(25)),
		'NR-SCS': int(match.group(26)),
		'AvgRSRP': int(match.group(27)),
		'AvgRSRQ': int(match.group(28)),
		'NRAntDiff': int(match.group(29)),
		'NRActANT': match.group(30),
		'TxPwr': int(match.group(31)),
		'TotalTxPwr': int(match.group(32)),
		'NumLayer': int(match.group(33)),
		'DL_BLER': int(match.group(34)),
		'PDSCH_RX0_SINR': int(match.group(35)),
		'PDSCH_RX1_SINR': int(match.group(36)),
		'PDSCH_RX2_SINR': int(match.group(37)),
		'PDSCH_RX3_SINR': int(match.group(38)),
		'DL_DRB': int(match.group(39)),
		'UL_DRB': int(match.group(40)),
#		'CID': int(match.group(41)),
#		'RRC': int(match.group(42)),
#		'5GMM_STATE': int(match.group(43)),
#		'GUTI': int(match.group(44)),
#		'TAC': int(match.group(45)),
#		'CDRX': int(match.group(46))
            }
            return nrds_values
        else:
            print("Failed to match NRDS pattern. Raw response:")
            print(response)
            return None

    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def save_to_csv(data):
    filename = f"nrds_values_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, 'w') as file:
        # Define widths
        parameter_width = 20
        value_width = 10
        
        # Write the header
        file.write(f"{'Parameter':<{parameter_width}}{'Value':<{value_width}}\n")
        file.write(f"{'-'*parameter_width}{'-'*value_width}\n")
        
        # Write the data
        for key, value in data.items():
            file.write(f"{key:<{parameter_width}}{value:<{value_width}}\n")
            
    return filename

def print_table(data):
    print("\n{:<20} {:<10}".format('Parameter', 'Value'))
    print("-" * 32)
    for key, value in data.items():
        print("{:<20} {:<10}".format(key, value))

if __name__ == "__main__":
    # Check if running with sudo
    if os.geteuid() != 0:
        print("This script requires sudo privileges to change port permissions.")
        print("Attempting to re-run with sudo...")
        try:
            subprocess.run(['sudo', sys.executable] + sys.argv, check=True)
            sys.exit(0)
        except subprocess.CalledProcessError:
            print("Failed to run with sudo. Please run the script manually with sudo.")
            sys.exit(1)

    # Example usage
    values = extract_nrds_values()
    if values:
        print("AT#NRDS values:")
        print_table(values)
        
        csv_filename = save_to_csv(values)
        print(f"\nData saved to CSV file: {csv_filename}")
    else:
        print("Failed to extract AT#NRDS values")

