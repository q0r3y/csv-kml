#!/usr/bin/python
'''
This code converts the csv file created during a
wardrive into a kml file usable by google earth.
It uses the pickle library to store the data after
it has been parsed for later usage that way there
is no need to parse massive csv files multiple times.
'''
# q0R3y

import pickle, re, csv, argparse, subprocess

# TODO:
# Add OPEN to the REPORT
# If PCKL exists DO NOT reparse everything

#Create command line parser object
parser = argparse.ArgumentParser(description='Converts CSV to KML for use with Google Earth')
#Creates command line parser arguments
parser.add_argument("-i", required=True, metavar='input file', type=str, help="-i to select CSV File")
parser.add_argument("-o", required=True, metavar='output file', type=str, help="-o to select KML File output.")
parser.add_argument("-r", default='n', metavar='y/N', type=str, help="-r to generate a report")
parser.add_argument("-e", default='n', metavar='y/N', type=str, help="-e executes the KML file in Google Earth")
#Parser Object Setups
args = parser.parse_args()
i = args.i
o = args.o
r = args.r
e = args.e
#KML Creation Code
def header():
    header =(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
            '  <Document>\n'
            )
    return header

def styles(SSID, secProtocol):

    colorDict ={'OPEN':'64F00014', # Blue
                'WEP':'641400FF',  # Red
                'WPA':'6414F0FF',  # Yellow
                'WPA2':'6400FF14'} # Green
    #regex to find security protocol
    regex = re.compile('WEP|WPA2|WPA')
    foundSecPro = regex.findall(secProtocol)

    if len(foundSecPro) < 1:
        foundSecPro.append('OPEN')

    normalStyle = (
            '    <Style id="'+str(SSID)+'_normal">\n'
            '      <IconStyle>\n'
            '        <color>'+str(colorDict[foundSecPro[-1]])+'</color>\n'
            '        <scale>1</scale>\n'
            '        <Icon>\n'
            '          <href>http://maps.google.com/mapfiles/kml/shapes/target.png</href>\n'
            '        </Icon>\n'
            '      </IconStyle>\n'
            '    </Style>\n')
    highlightStyle = (
            '    <Style id="'+str(SSID)+'_highlight">\n'
            '      <IconStyle>\n'
            '        <color>'+str(colorDict[foundSecPro[-1]])+'</color>\n'
            '        <scale>1</scale>\n'
            '          <Icon>\n'
            '            <href>http://maps.google.com/mapfiles/kml/shapes/target.png</href>\n'
            '          </Icon>\n'
            '      </IconStyle>\n'
            '    </Style>\n')
    styleMap = (
            '    <StyleMap id="'+str(SSID)+'_styleMap">\n'
            '       <Pair>\n'
            '         <key>normal</key>\n'
            '         <styleUrl>#'+str(SSID)+'_normal</styleUrl>\n'
            '       </Pair>\n'
            '       <Pair>\n'
            '         <key>highlight</key>\n'
            '         <styleUrl>#'+str(SSID)+'_highlight</styleUrl>\n'
            '       </Pair>\n'
            '   </StyleMap>\n')

    style = (normalStyle+highlightStyle+styleMap)
    return style

def body(SSID, BSSID, secProtocol, sigStr, freq, gpsAcc, long, lat):
    body = (
            '    <Placemark>\n'
            '      <name>'+str(SSID)+'</name>\n'
            '      <styleUrl>#'+str(SSID)+'_styleMap</styleUrl>\n'
            '      <description>\n'
            '        <![CDATA[\n'
            '	 <h2>BSSID: '+str(BSSID)+'<h2>\n'
            '	 <h2>SSID: '+str(SSID)+'<h2>\n'
            '	 <h2>Encryption: '+str(secProtocol)+'<h2>\n'
            '	 <h2>Signal Strength(-dBm): '+str(sigStr)+'<h2>\n'
            '	 <h2>Frequency: '+str(freq)+'<h2>\n'
            '	 <h2>GPS Accuracy: '+str(gpsAcc)+'<h2>\n'
            '	]]>\n'
            '      </description>\n'
            '      <Point>\n'
            '        <coordinates>'+str(long)+','+str(lat)+'</coordinates>\n'
            '      </Point>\n'
            '    </Placemark>\n'
            )
    return body

def footer():
    footer =(
            ' </Document>\n'
            '</kml>'
            )
    return footer
#KML Creation Code End
#-------------
#CSV Manipulation Code
def pcklCSV(csvFilePath):
    with open(str(csvFilePath), 'r') as csvFile:
        reader = csv.reader(csvFile, delimiter=',')
        allData = [[],[],[],[],[],[],[],[],[],[]]
        index = 0
        # Unix time : BSSID : Signal strength(-dBm): SSID : Longitude : Latitude : GPS Accuracy : AP Capabilities : Channel : Frequency
        # Appends each item in each row to the appropriate index in the allData variable
        for row in reader:
            counter = 0
            while counter <= (len(allData)-1):
                allData[index+counter].append(row[index+counter])
                counter += 1
        #Deletes CSV column header
        for row in allData:
            del row[0]
        #Create pckl file with allData variable
        f = open(str(csvFilePath+'.pckl'), 'wb')
        pickle.dump(allData, f)
        f.close()

def pcklOpen(pcklFilePath):
    f = open(pcklFilePath, 'rb')
    data = pickle.load(f)
    f.close()
    return data
#CSV Manipulation Code End

def ssidStrip(SSID):
    # Strips bad characters from SSID
    if '&' in SSID:
        ssidClean = SSID.replace('&', '_')
        return ssidClean
    else:
        return SSID

def ssidReport(SSID):
    #Counts each occurence of different security protocols
    secCount = [0,0,0]
    for item in SSID:
        if 'WPA2' in item:
            secCount[0] += 1
        elif 'WPA' in item:
            secCount[1] += 1
        elif 'WEP' in item:
            secCount[2] += 1
        else:
            pass
    print(' ')
    print(' ---- REPORT ----')
    print(' WPA2: '+str(secCount[0]))
    print(' WPA: '+str(secCount[1]))
    print(' WEP: '+str(secCount[2]))

def main():
    # if the command line argument (-i) is present
    if i:
        pcklCSV(i)
    data = pcklOpen(str(i+'.pckl'))
    # if the command line argument (-o) is present
    if o:
        kmlFile = open(str(o), 'w')

    kmlFile.write(header())
    counter = 0
    for element in data[0]:
        # Creates a formatted item for each access point in the CSV
        item = str(styles(ssidStrip(data[3][counter]), data[7][counter])+
        body(ssidStrip(data[3][counter]), data[1][counter], data[7][counter],
        data[2][counter], data[9][counter], data[6][counter],
        data[4][counter], data[5][counter]))
        # Appends that item to the KML file
        kmlFile.write(item)
        counter += 1
    kmlFile.write(footer())
    kmlFile.close()

    if r == 'y'.lower():
        # generates a report and prints it to console
        ssidReport(data[7])
        print(' TOTAL: '+str(counter))
        print(' ---- REPORT ---- ')
        print(' ')

    if e == 'y'.lower():
        # opens the kml output file in google earth
        subprocess.call(['xdg-open', o])

if __name__ == '__main__':
    main()

