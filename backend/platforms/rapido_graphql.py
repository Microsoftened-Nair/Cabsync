"""
Rapido API integration for fetching ride prices.
Uses the PWA API endpoint which returns protobuf wire format data.
"""
import requests
import json
import struct
from typing import Dict, List, Optional, Any

try:
    import blackboxprotobuf
    HAS_BLACKBOX = True
except ImportError:
    HAS_BLACKBOX = False
    print("Warning: blackboxprotobuf not installed. Install with: pip install blackboxprotobuf")


class RapidoAPIClient:
    """Client for Rapido's API to fetch ride prices."""
    
    BASE_URL = "https://m.rapido.bike/pwa/api/unup/scc/fareEstimate"
    
    def __init__(self):
        """Initialize the Rapido API client."""
        pass
        
    def get_ride_prices(
        self,
        pickup_lat: float,
        pickup_lng: float,
        pickup_display_name: str,
        pickup_address: str,
        dropoff_lat: float,
        dropoff_lng: float,
        dropoff_display_name: str,
        dropoff_address: str,
        device_id: str = "cabsync-aggregator"
    ) -> bytes:
        """
        Get ride prices from pickup to dropoff location.
        
        Args:
            pickup_lat: Pickup latitude
            pickup_lng: Pickup longitude
            pickup_display_name: Display name for pickup location
            pickup_address: Full address for pickup location
            dropoff_lat: Dropoff latitude
            dropoff_lng: Dropoff longitude
            dropoff_display_name: Display name for dropoff location
            dropoff_address: Full address for dropoff location
            device_id: Device identifier
            
        Returns:
            Raw protobuf bytes from the API
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/json',
            'channel-name': 'pwa',
            'channel-host': 'browser',
            'channel-entity': 'customer',
            'version': '1.0',
            'appid': '2',
            'appversion': '214',
            'authorization': 'Bearer',
            'Origin': 'https://m.rapido.bike',
        }
        
        payload = {
            "pickupLocation": {
                "lat": pickup_lat,
                "lng": pickup_lng,
                "displayName": pickup_display_name,
                "address": pickup_address
            },
            "dropLocation": {
                "lat": dropoff_lat,
                "lng": dropoff_lng,
                "displayName": dropoff_display_name,
                "address": dropoff_address
            },
            "deviceId": device_id
        }
        
        response = requests.post(
            self.BASE_URL,
            headers=headers,
            json=payload
        )
        
        response.raise_for_status()
        return response.content
    
    def decode_protobuf_response(self, protobuf_data: bytes) -> Dict[str, Any]:
        """
        Decode the protobuf wire format response from Rapido.
        
        The response comes as a JSON array of byte values which represents
        protobuf wire format data. This function decodes it into structured data.
        
        Args:
            protobuf_data: Raw protobuf bytes from the API
            
        Returns:
            Dictionary containing parsed ride options
        """
        try:
            # First, parse the JSON array of bytes
            byte_array = json.loads(protobuf_data.decode('utf-8'))
            
            # Convert to bytes
            wire_bytes = bytes(byte_array)
            
            if HAS_BLACKBOX:
                # Use blackboxprotobuf for proper decoding
                decoded_json, _ = blackboxprotobuf.protobuf_to_json(wire_bytes)
                return json.loads(decoded_json)
            else:
                # Fallback to manual parsing
                result = self._parse_protobuf_wire_format(wire_bytes)
                return result
            
        except Exception as e:
            print(f"Error decoding protobuf response: {e}")
            return {}
    
    def _parse_protobuf_wire_format(self, data: bytes) -> Dict[str, Any]:
        """
        Parse protobuf wire format data.
        
        Protobuf wire format uses variable-length encoding (varint) for field numbers
        and types. Each field is encoded as:
        - Tag (field_number << 3 | wire_type)
        - Length (for length-delimited types)
        - Value
        
        Wire types:
        0: Varint (int32, int64, uint32, uint64, sint32, sint64, bool, enum)
        1: 64-bit (fixed64, sfixed64, double)
        2: Length-delimited (string, bytes, embedded messages, packed repeated fields)
        5: 32-bit (fixed32, sfixed32, float)
        
        Args:
            data: Raw protobuf wire format bytes
            
        Returns:
            Parsed data structure
        """
        result = {
            'ride_options': [],
            'raw_data': data.hex()
        }
        
        pos = 0
        current_ride = {}
        
        while pos < len(data):
            # Read varint tag
            tag, pos = self._read_varint(data, pos)
            if tag == 0:
                break
                
            field_number = tag >> 3
            wire_type = tag & 0x07
            
            if wire_type == 0:  # Varint
                value, pos = self._read_varint(data, pos)
                self._store_field(current_ride, field_number, value, 'varint')
                
            elif wire_type == 1:  # 64-bit
                if pos + 8 <= len(data):
                    value = int.from_bytes(data[pos:pos+8], byteorder='little')
                    pos += 8
                    self._store_field(current_ride, field_number, value, '64bit')
                else:
                    break
                    
            elif wire_type == 2:  # Length-delimited
                length, pos = self._read_varint(data, pos)
                if pos + length <= len(data):
                    value = data[pos:pos+length]
                    pos += length
                    
                    # Try to decode as string
                    try:
                        str_value = value.decode('utf-8')
                        self._store_field(current_ride, field_number, str_value, 'string')
                    except:
                        # If not string, might be embedded message
                        self._store_field(current_ride, field_number, value.hex(), 'bytes')
                else:
                    break
                    
            elif wire_type == 5:  # 32-bit
                if pos + 4 <= len(data):
                    value = int.from_bytes(data[pos:pos+4], byteorder='little')
                    pos += 4
                    self._store_field(current_ride, field_number, value, '32bit')
                else:
                    break
            else:
                # Unknown wire type, skip
                break
        
        if current_ride:
            result['ride_options'].append(current_ride)
            
        return result
    
    def _read_varint(self, data: bytes, pos: int) -> tuple:
        """Read a varint from the data at position pos."""
        result = 0
        shift = 0
        
        while pos < len(data):
            byte = data[pos]
            result |= (byte & 0x7F) << shift
            pos += 1
            
            if (byte & 0x80) == 0:
                break
                
            shift += 7
            
        return result, pos
    
    def _store_field(self, obj: dict, field_num: int, value: Any, field_type: str):
        """Store a parsed field in the result object."""
        if field_num not in obj:
            obj[field_num] = []
        obj[field_num].append({
            'value': value,
            'type': field_type
        })
    
    def parse_ride_options(self, decoded_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse the decoded protobuf data into simplified ride options.
        
        Protobuf structure (discovered through reverse engineering):
        - Field "1": Status info (success/error)
        - Field "2": Main data container
          - Field "2.4": Array of ride options
            - Each ride has:
              - Field "1": Ride type ID
              - Field "2": Secondary ID  
              - Field "3": Base/min price (as double, 64-bit)
              - Field "4": Max price (as double, 64-bit)
        - Field "3": HTTP status code
        
        Args:
            decoded_data: Decoded protobuf data
            
        Returns:
            List of ride options with name, price, ETA, etc.
        """
        rides = []
        
        try:
            # Extract ride options from field 2.4
            main_data = decoded_data.get('2', {})
            ride_options = main_data.get('4', [])
            
            # Mapping of ride type IDs to names (discovered through testing)
            ride_type_names = {
                '5bd6c6e2e79cc313a94728d0': 'Rapido Auto',
                '5e8a15fe3c89412b94731fbb': 'Rapido Bike',
                '64253ccfc5df55a274d3565e': 'Rapido Cab Economy',
                '64253cb9c8ed60001752e182': 'Rapido Cab',
                '6759719ee6bfd0c631925d99': 'Rapido Premium',
            }
            
            for idx, option in enumerate(ride_options):
                ride_id = option.get('1', '')
                ride_name = ride_type_names.get(ride_id, f'Rapido Ride {idx + 1}')
                
                # Extract prices - they're stored as 64-bit IEEE 754 doubles
                price_min_val = option.get('3', '0')
                price_max_val = option.get('4', '0')
                
                try:
                    # Convert string to int, then to double
                    price_min_int = int(price_min_val)
                    price_max_int = int(price_max_val)
                    
                    # Unpack as IEEE 754 double
                    price_min = struct.unpack('d', struct.pack('Q', price_min_int))[0]
                    price_max = struct.unpack('d', struct.pack('Q', price_max_int))[0]
                    
                    # Format price range
                    if price_min == price_max:
                        price_str = f"₹{price_min:.0f}"
                    else:
                        price_str = f"₹{price_min:.0f}-{price_max:.0f}"
                        
                except (ValueError, struct.error) as e:
                    price_str = "N/A"
                    price_min = 0
                    price_max = 0
                
                ride = {
                    'name': ride_name,
                    'description': f'{ride_name} ride',
                    'price': price_str,
                    'price_min': price_min,
                    'price_max': price_max,
                    'currency': 'INR',
                    'eta': 'N/A',  # ETA not included in this response
                    'provider': 'Rapido',
                    'ride_id': ride_id,
                    'vehicle_type': self._get_vehicle_type(ride_name),
                }
                
                rides.append(ride)
                
        except Exception as e:
            print(f"Error parsing ride options: {e}")
            import traceback
            traceback.print_exc()
            
        return rides
    
    def _get_vehicle_type(self, ride_name: str) -> str:
        """Determine vehicle type from ride name."""
        name_lower = ride_name.lower()
        if 'bike' in name_lower:
            return 'bike'
        elif 'auto' in name_lower:
            return 'auto'
        elif 'cab' in name_lower or 'economy' in name_lower or 'premium' in name_lower:
            return 'car'
        return 'unknown'
    
    def get_and_parse_prices(
        self,
        pickup_lat: float,
        pickup_lng: float,
        pickup_name: str,
        dropoff_lat: float,
        dropoff_lng: float,
        dropoff_name: str
    ) -> List[Dict[str, Any]]:
        """
        Convenience method to get and parse prices in one call.
        
        Args:
            pickup_lat: Pickup latitude
            pickup_lng: Pickup longitude
            pickup_name: Pickup location name
            dropoff_lat: Dropoff latitude
            dropoff_lng: Dropoff longitude
            dropoff_name: Dropoff location name
            
        Returns:
            List of parsed ride options
        """
        # Get raw protobuf data
        protobuf_data = self.get_ride_prices(
            pickup_lat=pickup_lat,
            pickup_lng=pickup_lng,
            pickup_display_name=pickup_name,
            pickup_address=pickup_name,
            dropoff_lat=dropoff_lat,
            dropoff_lng=dropoff_lng,
            dropoff_display_name=dropoff_name,
            dropoff_address=dropoff_name
        )
        
        # Decode protobuf
        decoded_data = self.decode_protobuf_response(protobuf_data)
        
        # Parse into ride options
        rides = self.parse_ride_options(decoded_data)
        
        return rides


def main():
    """Example usage of the Rapido API client."""
    client = RapidoAPIClient()
    
    # Example: Get prices from Loni Kalbhor to Pune Railway Station
    pickup_lat = 18.4878505
    pickup_lng = 74.0234138
    pickup_name = "Loni Kalbhor, Maharashtra, India"
    
    dropoff_lat = 18.5288974
    dropoff_lng = 73.8665321
    dropoff_name = "PUNE RAILWAY STATION, Pune, Maharashtra, India"
    
    try:
        print(f"\n{'='*60}")
        print(f"Rapido Ride Options")
        print(f"From: {pickup_name}")
        print(f"To: {dropoff_name}")
        print(f"{'='*60}\n")
        
        # Get raw protobuf data
        protobuf_data = client.get_ride_prices(
            pickup_lat=pickup_lat,
            pickup_lng=pickup_lng,
            pickup_display_name=pickup_name,
            pickup_address=pickup_name,
            dropoff_lat=dropoff_lat,
            dropoff_lng=dropoff_lng,
            dropoff_display_name=dropoff_name,
            dropoff_address=dropoff_name
        )
        
        print(f"Received {len(protobuf_data)} bytes of protobuf data")
        print(f"First 100 bytes (hex): {protobuf_data[:100].hex()}")
        print()
        
        # Decode and parse
        decoded_data = client.decode_protobuf_response(protobuf_data)
        print(f"Decoded data: {json.dumps(decoded_data, indent=2)[:500]}...")
        print()
        
        rides = client.parse_ride_options(decoded_data)
        
        for ride in rides:
            print(f"{ride['name']:15} | {ride['price']:10} | ETA: {ride['eta']}")
            print(f"  Raw fields: {ride.get('raw_fields', {})}")
            print()
            
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
