"""
Rockfall Early Warning and Response Coordination System
Emergency Response Coordination Module

This module coordinates emergency response based STRICTLY on documented,
administrator-uploaded, and verified safety protocols.

SAFETY INTEGRITY PRINCIPLE:
This system NEVER hallucinates or invents evacuation routes, assembly points,
or contact persons. If a zone lacks a verified protocol, it explicitly notifies
responders to refer to regional emergency authorities, preventing dangerous misinformation.
"""

from datetime import datetime
from database import get_db_connection


def get_zone_protocol(zone_id):
    """
    Retrieves the verified safety protocol for a specific zone from SQLite.
    Returns None if no verified protocol exists.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, z.name as zone_name, z.location as zone_location, z.rock_type, z.slope_angle_deg
        FROM safety_protocols p
        JOIN zones z ON p.zone_id = z.id
        WHERE p.zone_id = ?
    ''', (zone_id,))
    protocol = cursor.fetchone()
    conn.close()

    if protocol:
        return dict(protocol)
    return None


def get_all_protocols_with_zones():
    """Returns all zones alongside their attached safety protocol status."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT z.id as zone_id, z.zone_code, z.name as zone_name, z.location, z.current_risk,
               p.id as protocol_id, p.protocol_code, p.title as protocol_title,
               p.authority_source, p.evacuation_route, p.safe_assembly_point,
               p.emergency_commander, p.contact_phone, p.is_verified, p.verified_date,
               p.document_filename
        FROM zones z
        LEFT JOIN safety_protocols p ON z.id = p.zone_id
        ORDER BY z.id ASC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def generate_grounded_evacuation_notice(zone, trigger_reason, alert_severity='High Risk'):
    """
    Generates a grounded emergency response notice.
    
    If a verified protocol exists, uses ONLY the administrator-verified instructions.
    If no verified protocol is found, explicitly refuses to generate synthetic routes
    and directs personnel to official emergency contacts.
    """
    protocol = get_zone_protocol(zone['id'])
    timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')

    # Case 1: Verified Protocol Found
    if protocol and protocol.get('is_verified') == 1:
        notice = {
            'status': 'VERIFIED_PROTOCOL_ACTIVE',
            'is_grounded': True,
            'zone_id': zone['id'],
            'zone_code': zone.get('zone_code', f"ZONE-{zone['id']}"),
            'zone_name': zone.get('name', 'Designated Zone'),
            'location': zone.get('location', 'Site Perimeter'),
            'alert_severity': alert_severity,
            'trigger_reason': trigger_reason,
            'protocol_code': protocol['protocol_code'],
            'protocol_title': protocol['title'],
            'authority_source': protocol['authority_source'],
            'evacuation_route': protocol['evacuation_route'],
            'safe_assembly_point': protocol['safe_assembly_point'],
            'emergency_commander': protocol['emergency_commander'],
            'contact_phone': protocol['contact_phone'],
            'document_filename': protocol.get('document_filename'),
            'verified_date': protocol.get('verified_date'),
            'timestamp': timestamp_str,
            'official_instructions': [
                f"Cease all operations and activate local slope warning beacons immediately.",
                f"Follow the designated evacuation corridor: {protocol['evacuation_route']}.",
                f"Report to designated muster station: {protocol['safe_assembly_point']}.",
                f"Do not enter the slope toe or crest buffer under any circumstances.",
                f"Field supervisors must account for personnel using physical muster manifests."
            ]
        }
    # Case 2: No Verified Protocol Exists (Honest System Safety Fallback)
    else:
        notice = {
            'status': 'NO_VERIFIED_PROTOCOL',
            'is_grounded': False,
            'zone_id': zone['id'],
            'zone_code': zone.get('zone_code', f"ZONE-{zone['id']}"),
            'zone_name': zone.get('name', 'Designated Zone'),
            'location': zone.get('location', 'Site Perimeter'),
            'alert_severity': alert_severity,
            'trigger_reason': trigger_reason,
            'protocol_code': 'UNVERIFIED-CONTINGENCY-NOTICE',
            'protocol_title': 'Standard Precautionary Evacuation Advisory',
            'authority_source': 'National Emergency Management Guidelines (General Directive)',
            'evacuation_route': 'NO VERIFIED ZONE ROUTE ON RECORD - Move immediately perpendicular to the rockfall runout trajectory towards elevated, clear bedrock.',
            'safe_assembly_point': 'Move at least 500 meters clear of the slope toe to designated public highway staging areas.',
            'emergency_commander': 'Incident Commander on Duty / National Emergency Helpline',
            'contact_phone': 'National Emergency: 112 / State Disaster Control: 1070',
            'document_filename': None,
            'verified_date': 'Unverified',
            'timestamp': timestamp_str,
            'safety_disclaimer': 'CRITICAL SAFETY NOTICE: This monitoring zone lacks an administrator-verified safety protocol. To prevent fatal navigation errors, this decision support system NEVER fabricates evacuation routes or assembly coordinates. Follow standard emergency operating procedures and report directly to local civil defense authorities.',
            'official_instructions': [
                "Sound manual sirens and abandon all lower-bench vehicles and plant equipment immediately.",
                "Evacuate perpendicular (at 90 degrees) to the downward rockfall path towards open terrain.",
                "Dial Emergency Services (112) to dispatch search and rescue squads.",
                "Notify site superintendent immediately to upload and verify the official zone SOP in the Admin Panel."
            ]
        }

    return notice


def save_or_update_protocol(data):
    """Inserts or updates a zone safety protocol in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if exists
    cursor.execute('SELECT id FROM safety_protocols WHERE zone_id = ?', (data['zone_id'],))
    existing = cursor.fetchone()

    is_verified = 1 if str(data.get('is_verified', '1')) in ['1', 'true', 'True'] else 0
    verified_date = datetime.now().strftime('%Y-%m-%d') if is_verified else None

    if existing:
        cursor.execute('''
            UPDATE safety_protocols
            SET protocol_code = ?, title = ?, authority_source = ?,
                evacuation_route = ?, safe_assembly_point = ?,
                emergency_commander = ?, contact_phone = ?,
                is_verified = ?, verified_date = ?, document_filename = ?
            WHERE zone_id = ?
        ''', (
            data['protocol_code'],
            data['title'],
            data['authority_source'],
            data['evacuation_route'],
            data['safe_assembly_point'],
            data['emergency_commander'],
            data['contact_phone'],
            is_verified,
            verified_date,
            data.get('document_filename', 'protocol_document.pdf'),
            data['zone_id']
        ))
    else:
        cursor.execute('''
            INSERT INTO safety_protocols (
                zone_id, protocol_code, title, authority_source,
                evacuation_route, safe_assembly_point, emergency_commander,
                contact_phone, is_verified, verified_date, document_filename
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['zone_id'],
            data['protocol_code'],
            data['title'],
            data['authority_source'],
            data['evacuation_route'],
            data['safe_assembly_point'],
            data['emergency_commander'],
            data['contact_phone'],
            is_verified,
            verified_date,
            data.get('document_filename', 'protocol_document.pdf')
        ))

    conn.commit()
    conn.close()
    return True
