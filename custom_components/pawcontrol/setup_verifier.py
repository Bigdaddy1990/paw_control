"""Setup verification and auto-fix functionality for Paw Control with enhanced Hundesystem GPS/health support."""
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

_LOGGER = logging.getLogger(__name__)

async def async_verify_critical_entities(hass, dog_name):
    """Verify that critical entities exist and are functional."""
    critical_entities = [
        f"input_boolean.{dog_name}_feeding_morning",
        f"input_boolean.{dog_name}_feeding_evening",
        f"input_boolean.{dog_name}_outside",
        f"counter.{dog_name}_outside_count",
        f"input_text.{dog_name}_notes",
        f"input_datetime.{dog_name}_last_outside",
        f"input_select.{dog_name}_health_status",
        f"input_number.{dog_name}_weight",
    ]
    verification_result = {
        "critical_entities_total": len(critical_entities),
        "critical_entities_found": 0,
        "critical_entities_missing": [],
        "critical_entities_working": [],
        "critical_entities_broken": [],
        "is_functional": False
    }
    try:
        for entity_id in critical_entities:
            state = hass.states.get(entity_id)
            if not state:
                verification_result["critical_entities_missing"].append(entity_id)
                continue
            verification_result["critical_entities_found"] += 1
            if state.state in ["unknown", "unavailable"]:
                verification_result["critical_entities_broken"].append(entity_id)
            else:
                verification_result["critical_entities_working"].append(entity_id)
        working_count = len(verification_result["critical_entities_working"])
        total_count = len(critical_entities)
        verification_result["is_functional"] = (working_count / total_count) >= 0.8  # 80% threshold
        _LOGGER.info("Critical entity verification for %s: %d/%d working (%.1f%%)", 
                    dog_name, working_count, total_count, (working_count / total_count) * 100)
        return verification_result
    except Exception as e:
        _LOGGER.error("Error during critical entity verification: %s", e)
        return {
            **verification_result,
            "error": str(e),
            "is_functional": False
        }

async def async_repair_broken_entities(hass, dog_name, get_expected_entities):
    """Attempt to repair broken entities by recreating them."""
    repair_result = {
        "entities_checked": 0,
        "entities_repaired": 0,
        "entities_failed": 0,
        "repaired_entities": [],
        "failed_entities": [],
        "repair_actions": []
    }
    try:
        expected_entities = await get_expected_entities(dog_name)
        for entity_id, entity_info in expected_entities.items():
            repair_result["entities_checked"] += 1
            state = hass.states.get(entity_id)
            needs_repair = False
            repair_reason = ""
            if not state:
                needs_repair = True
                repair_reason = "Entity does not exist"
            elif state.state in ["unknown", "unavailable"]:
                needs_repair = True
                repair_reason = f"Entity in invalid state: {state.state}"
            elif not state.attributes.get("friendly_name"):
                needs_repair = True
                repair_reason = "Missing friendly name"
            if needs_repair:
                _LOGGER.info("Repairing entity %s: %s", entity_id, repair_reason)
                try:
                    # Remove existing entity if it exists but is broken
                    if state:
                        try:
                            await hass.services.async_call(
                                entity_info["domain"], "remove", 
                                {"entity_id": entity_id}, 
                                blocking=True
                            )
                            await asyncio.sleep(1.0)
                        except Exception as remove_error:
                            _LOGGER.debug("Could not remove broken entity %s: %s", entity_id, remove_error)
                    # Recreate the entity
                    missing_entity = {
                        "entity_id": entity_id,
                        "domain": entity_info["domain"],
                        "friendly_name": entity_info["friendly_name"],
                        "icon": entity_info.get("icon"),
                        "config": entity_info.get("config", {})
                    }
                    # Use the new _create_missing_entity function!
                    from .setup_verifier import _create_missing_entity
                    success = await _create_missing_entity(hass, missing_entity, dog_name)
                    if success:
                        repair_result["entities_repaired"] += 1
                        repair_result["repaired_entities"].append(entity_id)
                        repair_result["repair_actions"].append(f"Repaired {entity_id}: {repair_reason}")
                        _LOGGER.info("✅ Successfully repaired: %s", entity_id)
                    else:
                        repair_result["entities_failed"] += 1
                        repair_result["failed_entities"].append(entity_id)
                        repair_result["repair_actions"].append(f"Failed to repair {entity_id}: {repair_reason}")
                        _LOGGER.error("❌ Failed to repair: %s", entity_id)
                except Exception as repair_error:
                    repair_result["entities_failed"] += 1
                    repair_result["failed_entities"].append(entity_id)
                    error_msg = f"Exception repairing {entity_id}: {str(repair_error)}"
                    repair_result["repair_actions"].append(error_msg)
                    _LOGGER.error("❌ %s", error_msg)
                await asyncio.sleep(0.5)
        _LOGGER.info("Entity repair completed for %s: %d repaired, %d failed", 
                    dog_name, repair_result["entities_repaired"], repair_result["entities_failed"])
        return repair_result
    except Exception as e:
        _LOGGER.error("Critical error during entity repair: %s", e)
        return {
            **repair_result,
            "error": str(e)
        }

async def async_generate_installation_report(hass, dog_name, async_verify_and_fix_installation, async_verify_critical_entities):
    """Generate a comprehensive installation report."""
    try:
        _LOGGER.info("Generating installation report for %s", dog_name)
        verification_result = await async_verify_and_fix_installation(hass, dog_name)
        critical_check = await async_verify_critical_entities(hass, dog_name)
        report = f"""
# 🐕 Paw Control Installation Report - {dog_name.title()}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 Overview
- **Status:** {verification_result.get('status', 'unknown').upper()}
- **Success Rate:** {verification_result.get('success_rate', 0):.1f}%
- **Total Expected Entities:** {verification_result.get('total_entities_expected', 0)}
- **Total Found Entities:** {verification_result.get('total_entities_found', 0)}

## 🎯 Critical Entities Status
- **Critical Entities Working:** {critical_check.get('critical_entities_found', 0)}/{critical_check.get('critical_entities_total', 0)}
- **Installation Functional:** {'✅ YES' if critical_check.get('is_functional') else '❌ NO'}

## 🔧 Auto-Fix Results
"""
        if verification_result.get('created_entities'):
            report += f"- **Entities Created:** {len(verification_result['created_entities'])}\n"
            for entity in verification_result['created_entities'][:10]:
                report += f"  - ✅ {entity}\n"
            if len(verification_result['created_entities']) > 10:
                report += f"  - ... and {len(verification_result['created_entities']) - 10} more\n"
        else:
            report += "- **No entities needed to be created**\n"
        if verification_result.get('errors'):
            report += f"\n## ❌ Errors ({len(verification_result['errors'])})\n"
            for error in verification_result['errors'][:5]:
                report += f"- {error}\n"
            if len(verification_result['errors']) > 5:
                report += f"- ... and {len(verification_result['errors']) - 5} more errors\n"
        if verification_result.get('missing_entities'):
            report += f"\n## 🚫 Still Missing Entities ({len(verification_result['missing_entities'])})\n"
            for entity in verification_result['missing_entities'][:10]:
                report += f"- {entity}\n"
            if len(verification_result['missing_entities']) > 10:
                report += f"- ... and {len(verification_result['missing_entities']) - 10} more\n"
        report += "\n## 💡 Recommendations\n"
        if verification_result.get('success_rate', 0) >= 95:
            report += "- ✅ Installation is excellent! All systems ready.\n"
        elif verification_result.get('success_rate', 0) >= 80:
            report += "- ⚡ Installation is good. Minor issues auto-fixed.\n"
        elif verification_result.get('success_rate', 0) >= 60:
            report += "- ⚠️ Installation has some issues. Consider manual intervention.\n"
        else:
            report += "- 🚨 Installation has significant problems. Manual setup may be required.\n"
        if not critical_check.get('is_functional'):
            report += "- 🔧 Critical entities are missing. Run verification again or recreate integration.\n"
        report += "\n---\n*Report generated by Paw Control v1.0 for {dog_name}*"
        return report
    except Exception as e:
        _LOGGER.error("Error generating installation report: %s", e)
        return f"# Error Generating Report\n\nAn error occurred: {str(e)}"

async def async_cleanup_duplicate_entities(hass, dog_name):
    """Clean up any duplicate entities that might exist."""
    cleanup_result = {
        "duplicates_found": 0,
        "duplicates_removed": 0,
        "cleanup_errors": [],
        "cleaned_entities": []
    }
    try:
        all_entities = hass.states.async_all()
        dog_entities = []
        for state in all_entities:
            entity_id = state.entity_id
            if dog_name in entity_id.lower():
                dog_entities.append(entity_id)
        potential_duplicates = []
        checked_entities = set()
        for entity_id in dog_entities:
            if entity_id in checked_entities:
                continue
            base_name = entity_id.lower().replace("_1", "").replace("_2", "").replace("_copy", "")
            similar_entities = []
            for other_entity in dog_entities:
                if other_entity != entity_id and base_name in other_entity.lower():
                    similar_entities.append(other_entity)
            if similar_entities:
                potential_duplicates.append({
                    "base": entity_id,
                    "duplicates": similar_entities
                })
                checked_entities.update([entity_id] + similar_entities)
        cleanup_result["duplicates_found"] = len(potential_duplicates)
        for duplicate_group in potential_duplicates:
            duplicates_to_remove = duplicate_group["duplicates"]
            for duplicate_entity in duplicates_to_remove:
                try:
                    domain = duplicate_entity.split('.')[0]
                    await hass.services.async_call(
                        domain, "remove",
                        {"entity_id": duplicate_entity},
                        blocking=True
                    )
                    cleanup_result["duplicates_removed"] += 1
                    cleanup_result["cleaned_entities"].append(duplicate_entity)
                    _LOGGER.info("Removed duplicate entity: %s", duplicate_entity)
                except Exception as e:
                    error_msg = f"Failed to remove duplicate {duplicate_entity}: {str(e)}"
                    cleanup_result["cleanup_errors"].append(error_msg)
                    _LOGGER.error("❌ %s", error_msg)
        _LOGGER.info("Duplicate cleanup completed for %s: %d removed, %d errors", 
                    dog_name, cleanup_result["duplicates_removed"], len(cleanup_result["cleanup_errors"]))
        return cleanup_result
    except Exception as e:
        _LOGGER.error("Error during duplicate cleanup: %s", e)
        return {
            **cleanup_result,
            "error": str(e)
        }
        
async def async_verify_and_fix_installation(hass: HomeAssistant, dog_name: str) -> Dict[str, Any]:
    """Verify Paw Control installation and auto-fix any issues (enhanced Hundesystem support)."""
    try:
        _LOGGER.info("🔍 Starting installation verification for %s", dog_name)
        
        verification_result = {
            "status": "unknown",
            "dog_name": dog_name,
            "total_entities_expected": 0,
            "total_entities_found": 0,
            "missing_entities": [],
            "created_entities": [],
            "errors": [],
            "success_rate": 0.0,
            "verification_timestamp": datetime.now().isoformat()
        }
        
        # Define all expected entities (merged model)
        expected_entities = await _get_expected_entities(dog_name)
        verification_result["total_entities_expected"] = len(expected_entities)
        
        # Check which entities exist
        existing_entities = []
        missing_entities = []
        
        for entity_id, entity_info in expected_entities.items():
            if hass.states.get(entity_id):
                existing_entities.append(entity_id)
            else:
                missing_entities.append({
                    "entity_id": entity_id,
                    "domain": entity_info["domain"],
                    "friendly_name": entity_info["friendly_name"],
                    "icon": entity_info.get("icon", "mdi:dog"),
                    "config": entity_info.get("config", {})
                })
        
        verification_result["total_entities_found"] = len(existing_entities)
        verification_result["missing_entities"] = [e["entity_id"] for e in missing_entities]
        verification_result["success_rate"] = (len(existing_entities) / len(expected_entities)) * 100 if expected_entities else 0
        
        _LOGGER.info("📊 Initial verification: %d/%d entities found (%.1f%%)", 
                    len(existing_entities), len(expected_entities), 
                    verification_result["success_rate"])
        
        # Auto-fix missing entities
        if missing_entities:
            _LOGGER.info("🔧 Auto-fixing %d missing entities...", len(missing_entities))
            
            created_entities = []
            fix_errors = []
            
            for missing_entity in missing_entities:
                try:
                    success = await _create_missing_entity(hass, missing_entity, dog_name)
                    if success:
                        created_entities.append(missing_entity["entity_id"])
                        _LOGGER.debug("✅ Created: %s", missing_entity["entity_id"])
                    else:
                        fix_errors.append(f"Failed to create {missing_entity['entity_id']}")
                        
                except Exception as e:
                    error_msg = f"Error creating {missing_entity['entity_id']}: {str(e)}"
                    fix_errors.append(error_msg)
                    _LOGGER.error("❌ %s", error_msg)
                
                # Brief pause between entity creations
                await asyncio.sleep(0.5)
            
            verification_result["created_entities"] = created_entities
            verification_result["errors"] = fix_errors
            
            # Update statistics
            total_now_existing = verification_result["total_entities_found"] + len(created_entities)
            verification_result["total_entities_found"] = total_now_existing
            verification_result["success_rate"] = (total_now_existing / len(expected_entities)) * 100 if expected_entities else 0
            
            _LOGGER.info("🔧 Auto-fix completed: %d entities created, %d errors", 
                        len(created_entities), len(fix_errors))
        
        # Determine final status
        if verification_result["success_rate"] >= 100.0:
            verification_result["status"] = "success"
        elif verification_result["success_rate"] >= 80.0 and verification_result["created_entities"]:
            verification_result["status"] = "fixed"
        elif verification_result["success_rate"] >= 50.0:
            verification_result["status"] = "partial"
        else:
            verification_result["status"] = "failed"
        
        # Set smart defaults (e.g. Detmold GPS) after entity creation
        await _set_smart_default_values(hass, dog_name)
        
        _LOGGER.info("🎯 Final verification result for %s: %s (%.1f%% success)", 
                    dog_name, verification_result["status"], verification_result["success_rate"])
        
        return verification_result
        
    except Exception as e:
        _LOGGER.error("❌ Critical error during installation verification: %s", e)
        return {
            "status": "error",
            "dog_name": dog_name,
            "error": str(e),
            "verification_timestamp": datetime.now().isoformat()
        }

# =========================
# Enhanced Entity Model
# =========================

async def _get_expected_entities(dog_name: str) -> Dict[str, Dict[str, Any]]:
    """Get dictionary of all expected entities for a dog, including enhanced GPS/health (Hundesystem)."""

    expected_entities = {}

    # --- Input Boolean entities ---
    input_booleans = [
        # Core feeding and activity
        (f"{dog_name}_feeding_morning", "Frühstück", "mdi:food"),
        (f"{dog_name}_feeding_lunch", "Mittagessen", "mdi:food"),
        (f"{dog_name}_feeding_evening", "Abendessen", "mdi:food"),
        (f"{dog_name}_feeding_snack", "Leckerli", "mdi:bone"),
        (f"{dog_name}_outside", "War draußen", "mdi:tree"),
        (f"{dog_name}_was_dog", "War es der Hund?", "mdi:dog"),
        (f"{dog_name}_poop_done", "Geschäft gemacht", "mdi:delete"),
        # GPS tracking
        (f"{dog_name}_walk_in_progress", "Spaziergang aktiv", "mdi:walk"),
        (f"{dog_name}_auto_walk_detection", "Auto-Spaziergang Erkennung", "mdi:radar"),
        (f"{dog_name}_gps_tracking_enabled", "GPS-Tracking aktiviert", "mdi:crosshairs-gps"),
        # Status
        (f"{dog_name}_visitor_mode_input", "Besuchsmodus", "mdi:account-group"),
        (f"{dog_name}_emergency_mode", "Notfallmodus", "mdi:alert"),
        (f"{dog_name}_medication_given", "Medikament gegeben", "mdi:pill"),
        (f"{dog_name}_feeling_well", "Fühlt sich wohl", "mdi:heart-pulse"),
        (f"{dog_name}_appetite_normal", "Normaler Appetit", "mdi:food"),
        (f"{dog_name}_energy_normal", "Normale Energie", "mdi:flash"),
        (f"{dog_name}_auto_reminders", "Automatische Erinnerungen", "mdi:bell"),
        (f"{dog_name}_tracking_enabled", "Tracking aktiviert", "mdi:map-marker"),
        (f"{dog_name}_weather_alerts", "Wetter-Warnungen", "mdi:weather-partly-cloudy"),
    ]
    for entity_name, friendly_name, icon in input_booleans:
        expected_entities[f"input_boolean.{entity_name}"] = {
            "domain": "input_boolean",
            "friendly_name": f"{dog_name.title()} {friendly_name}",
            "icon": icon,
            "config": {"icon": icon}
        }

    # --- Input Number entities ---
    numbers = [
        # GPS & Walk metrics
        (f"{dog_name}_current_walk_distance", "Aktuelle Spaziergang Distanz", 0.01, 0, 20, 0, "km", "mdi:map-marker-distance"),
        (f"{dog_name}_current_walk_duration", "Aktuelle Spaziergang Dauer", 1, 0, 300, 0, "min", "mdi:clock"),
        (f"{dog_name}_current_walk_speed", "Aktuelle Geschwindigkeit", 0.1, 0, 15, 0, "km/h", "mdi:speedometer"),
        (f"{dog_name}_walk_distance_today", "Heutige Spaziergang Distanz", 0.1, 0, 30, 0, "km", "mdi:map-marker-distance"),
        (f"{dog_name}_walk_distance_weekly", "Wöchentliche Gehstrecke", 0.1, 0, 200, 0, "km", "mdi:map-marker-distance"),
        (f"{dog_name}_walk_distance_monthly", "Monatliche Gehstrecke", 0.1, 0, 900, 0, "km", "mdi:map-marker-distance"),
        (f"{dog_name}_max_distance_from_home", "Max. Entfernung von Zuhause", 0.1, 0, 10, 5, "km", "mdi:map-marker-distance"),
        (f"{dog_name}_average_walk_speed", "Durchschnittliche Gehgeschwindigkeit", 0.1, 0, 10, 0, "km/h", "mdi:speedometer"),
        (f"{dog_name}_walks_count_today", "Spaziergänge heute", 1, 0, 10, 0, "", "mdi:walk"),
        (f"{dog_name}_walks_count_weekly", "Spaziergänge diese Woche", 1, 0, 50, 0, "", "mdi:walk"),
        (f"{dog_name}_calories_burned_walk", "Verbrannte Kalorien Spaziergang", 10, 0, 2000, 0, "kcal", "mdi:fire"),
        (f"{dog_name}_steps_count_estimated", "Geschätzte Schritte", 100, 0, 50000, 0, "Schritte", "mdi:shoe-print"),
        (f"{dog_name}_gps_battery_level", "GPS-Tracker Akku", 1, 0, 100, 100, "%", "mdi:battery"),
        (f"{dog_name}_gps_signal_strength", "GPS-Signalstärke", 1, 0, 100, 100, "%", "mdi:signal"),
        # Health
        (f"{dog_name}_weight", "Gewicht", 0.1, 0, 80, 15, "kg", "mdi:weight-kilogram"),
        (f"{dog_name}_temperature", "Körpertemperatur", 0.1, 35, 42, 38.5, "°C", "mdi:thermometer"),
        (f"{dog_name}_heart_rate", "Herzfrequenz", 1, 60, 200, 100, "bpm", "mdi:heart-pulse"),
        (f"{dog_name}_health_score", "Gesundheits Score", 1, 0, 10, 8, "", "mdi:heart-pulse"),
        (f"{dog_name}_happiness_score", "Glücks Score", 1, 0, 10, 8, "", "mdi:emoticon-happy"),
        (f"{dog_name}_energy_level", "Energie Level", 1, 0, 10, 8, "", "mdi:flash"),
        (f"{dog_name}_appetite_score", "Appetit Score", 1, 0, 10, 8, "", "mdi:food"),
        # Activity
        (f"{dog_name}_daily_walk_duration", "Tägliche Spaziergang Dauer", 1, 0, 300, 0, "min", "mdi:walk"),
        (f"{dog_name}_daily_play_time", "Tägliche Spielzeit", 1, 0, 180, 0, "min", "mdi:tennis"),
        (f"{dog_name}_training_duration", "Trainingsdauer", 1, 0, 120, 0, "min", "mdi:school"),
        (f"{dog_name}_daily_food_amount", "Tägliche Futtermenge", 10, 0, 2000, 400, "g", "mdi:food"),
        (f"{dog_name}_treat_amount", "Leckerli Menge", 5, 0, 200, 20, "g", "mdi:bone"),
        (f"{dog_name}_water_intake", "Wasseraufnahme", 50, 0, 3000, 500, "ml", "mdi:cup-water"),
        # Age/medication
        (f"{dog_name}_age_years", "Alter (Jahre)", 0.1, 0, 20, 3, "Jahre", "mdi:cake-variant"),
        (f"{dog_name}_age_months", "Alter (Monate)", 1, 0, 240, 36, "Monate", "mdi:cake-variant"),
        (f"{dog_name}_medication_dosage", "Medikament Dosis", 0.5, 0, 500, 5, "mg", "mdi:pill"),
    ]
    for entity_name, friendly_name, step, min_val, max_val, initial, unit, icon in numbers:
        expected_entities[f"input_number.{entity_name}"] = {
            "domain": "input_number",
            "friendly_name": f"{dog_name.title()} {friendly_name}",
            "icon": icon,
            "config": {
                "min": min_val,
                "max": max_val,
                "step": step,
                "initial": initial,
                "unit_of_measurement": unit,
                "icon": icon,
                "mode": "slider"
            }
        }

    # --- Input Text entities ---
    texts = [
        # GPS & Location
        (f"{dog_name}_current_location", "Aktueller Standort", 100, "mdi:map-marker"),
        (f"{dog_name}_last_known_location", "Letzter bekannter Standort", 100, "mdi:map-marker"),
        (f"{dog_name}_home_coordinates", "Zuhause Koordinaten", 50, "mdi:home-map-marker"),
        (f"{dog_name}_current_walk_route", "Aktuelle Spaziergang-Route", 2000, "mdi:map-marker-path"),
        (f"{dog_name}_favorite_walk_locations", "Lieblings-Spaziergänge", 500, "mdi:star"),
        (f"{dog_name}_walk_history_today", "Heutige Spaziergang-Historie", 2000, "mdi:history"),
        (f"{dog_name}_gps_tracker_id", "GPS-Tracker ID", 50, "mdi:crosshairs-gps"),
        (f"{dog_name}_geofence_alerts", "Geofence Benachrichtigungen", 255, "mdi:bell"),
        (f"{dog_name}_walk_statistics_summary", "Spaziergang-Statistiken", 2000, "mdi:chart-box"),
        (f"{dog_name}_gps_tracker_status", "GPS-Tracker Status", 255, "mdi:crosshairs-gps"),
        # Various notes, contacts, status, etc.
        (f"{dog_name}_notes", "Allgemeine Notizen", 255, "mdi:note-text"),
        (f"{dog_name}_daily_notes", "Tagesnotizen", 255, "mdi:note-text"),
        (f"{dog_name}_behavior_notes", "Verhaltensnotizen", 255, "mdi:note-text"),
        (f"{dog_name}_last_activity_notes", "Letzte Aktivität Notizen", 255, "mdi:note-text"),
        (f"{dog_name}_walk_notes", "Spaziergang Notizen", 255, "mdi:note-text"),
        (f"{dog_name}_play_notes", "Spiel Notizen", 255, "mdi:note-text"),
        (f"{dog_name}_training_notes", "Training Notizen", 255, "mdi:note-text"),
        (f"{dog_name}_health_notes", "Gesundheitsnotizen", 500, "mdi:heart-pulse"),
        (f"{dog_name}_medication_notes", "Medikamentenotizen", 255, "mdi:pill"),
        (f"{dog_name}_vet_notes", "Tierarztnotizen", 255, "mdi:stethoscope"),
        (f"{dog_name}_symptoms", "Symptome", 255, "mdi:emoticon-sad"),
        (f"{dog_name}_emergency_contact", "Notfallkontakt", 150, "mdi:phone"),
        (f"{dog_name}_vet_contact", "Tierarztkontakt", 150, "mdi:phone"),
        (f"{dog_name}_backup_contact", "Backup-Kontakt", 150, "mdi:phone"),
        (f"{dog_name}_breed", "Rasse", 100, "mdi:dog"),
        (f"{dog_name}_color", "Farbe/Markierungen", 100, "mdi:palette"),
        (f"{dog_name}_microchip_id", "Mikrochip ID", 50, "mdi:barcode"),
        (f"{dog_name}_insurance_number", "Versicherungsnummer", 50, "mdi:card-account-details"),
        (f"{dog_name}_visitor_name", "Besucher Name", 150, "mdi:account"),
        (f"{dog_name}_visitor_contact", "Besucher Kontakt", 150, "mdi:phone"),
        (f"{dog_name}_visitor_notes", "Besucher Notizen", 255, "mdi:note-text"),
        (f"{dog_name}_food_brand", "Futtermarke", 150, "mdi:food"),
        (f"{dog_name}_food_allergies", "Futterallergien", 255, "mdi:alert"),
        (f"{dog_name}_favorite_treats", "Lieblings-Leckerlis", 150, "mdi:bone"),
        (f"{dog_name}_current_mood", "Aktuelle Stimmung", 50, "mdi:emoticon-happy"),
        (f"{dog_name}_weather_preference", "Wetterpräferenz", 50, "mdi:weather-sunny"),
        (f"{dog_name}_special_instructions", "Besondere Anweisungen", 500, "mdi:note-text"),
        (f"{dog_name}_vaccination_records", "Impfaufzeichnungen", 500, "mdi:needle"),
        (f"{dog_name}_vaccination_vet_name", "Impfender Tierarzt", 100, "mdi:doctor"),
        (f"{dog_name}_vaccination_certificate_number", "Impfzertifikat Nummer", 50, "mdi:file-certificate"),
    ]
    for entity_name, friendly_name, max_length, icon in texts:
        expected_entities[f"input_text.{entity_name}"] = {
            "domain": "input_text",
            "friendly_name": f"{dog_name.title()} {friendly_name}",
            "icon": icon,
            "config": {
                "max": max_length,
                "initial": "",
                "icon": icon,
                "mode": "text"
            }
        }

    # --- Input Datetime entities ---
    datetimes = [
        (f"{dog_name}_last_walk", "Letzter Spaziergang", True, True, None, "mdi:walk"),
        (f"{dog_name}_last_feeding_morning", "Letztes Frühstück", True, True, None, "mdi:food"),
        (f"{dog_name}_last_feeding_lunch", "Letztes Mittagessen", True, True, None, "mdi:food"),
        (f"{dog_name}_last_feeding_evening", "Letztes Abendessen", True, True, None, "mdi:food"),
        (f"{dog_name}_last_feeding_snack", "Letztes Leckerli", True, True, None, "mdi:bone"),
        (f"{dog_name}_last_outside", "Letztes Mal draußen", True, True, None, "mdi:tree"),
        (f"{dog_name}_last_play", "Letztes Spielen", True, True, None, "mdi:tennis"),
        (f"{dog_name}_last_training", "Letztes Training", True, True, None, "mdi:school"),
        (f"{dog_name}_last_poop", "Letztes Geschäft", True, True, None, "mdi:delete"),
        (f"{dog_name}_last_activity", "Letzte Aktivität", True, True, None, "mdi:star"),
        (f"{dog_name}_last_door_ask", "Letztes Tür-Anfordern", True, True, None, "mdi:door"),
        # Feeding schedule times
        (f"{dog_name}_feeding_morning_time", "Frühstückszeit", False, True, "07:00:00", "mdi:clock"),
        (f"{dog_name}_feeding_lunch_time", "Mittagszeit", False, True, "12:00:00", "mdi:clock"),
        (f"{dog_name}_feeding_evening_time", "Abendzeit", False, True, "18:00:00", "mdi:clock"),
        # Appointments
        (f"{dog_name}_last_vet_visit", "Letzter Tierarztbesuch", True, True, None, "mdi:stethoscope"),
        (f"{dog_name}_next_vet_appointment", "Nächster Tierarzttermin", True, True, None, "mdi:stethoscope"),
        (f"{dog_name}_last_vaccination", "Letzte Impfung", True, True, None, "mdi:needle"),
        (f"{dog_name}_next_vaccination", "Nächste Impfung", True, True, None, "mdi:needle"),
        (f"{dog_name}_medication_time", "Medikamentenzeit", False, True, "08:00:00", "mdi:pill"),
        (f"{dog_name}_last_grooming", "Letzte Fellpflege", True, True, None, "mdi:shower"),
        (f"{dog_name}_next_grooming", "Nächste Fellpflege", True, True, None, "mdi:shower"),
        # Vaccination timeline
        (f"{dog_name}_last_rabies_vaccination", "Letzte Tollwutimpfung", True, True, None, "mdi:needle"),
        (f"{dog_name}_next_rabies_vaccination", "Nächste Tollwutimpfung", True, True, None, "mdi:needle"),
        (f"{dog_name}_last_distemper_vaccination", "Letzte Staupeimpfung", True, True, None, "mdi:needle"),
        (f"{dog_name}_next_distemper_vaccination", "Nächste Staupeimpfung", True, True, None, "mdi:needle"),
        (f"{dog_name}_last_hepatitis_vaccination", "Letzte Hepatitisimpfung", True, True, None, "mdi:needle"),
        (f"{dog_name}_next_hepatitis_vaccination", "Nächste Hepatitisimpfung", True, True, None, "mdi:needle"),
        # Special events
        (f"{dog_name}_emergency_contact_time", "Notfallkontaktzeit", True, True, None, "mdi:clock"),
        (f"{dog_name}_visitor_start", "Besuchsbeginn", True, True, None, "mdi:account-clock"),
        (f"{dog_name}_visitor_end", "Besuchsende", True, True, None, "mdi:account-clock"),
    ]
    for entity_name, friendly_name, has_date, has_time, initial, icon in datetimes:
        config = {
            "has_date": has_date,
            "has_time": has_time,
            "icon": icon
        }
        if initial:
            config["initial"] = initial
        expected_entities[f"input_datetime.{entity_name}"] = {
            "domain": "input_datetime",
            "friendly_name": f"{dog_name.title()} {friendly_name}",
            "icon": icon,
            "config": config
        }

    # --- Counter entities ---
    counters = [
        (f"{dog_name}_feeding_morning_count", "Frühstück Anzahl", "mdi:food"),
        (f"{dog_name}_feeding_lunch_count", "Mittagessen Anzahl", "mdi:food"),
        (f"{dog_name}_feeding_evening_count", "Abendessen Anzahl", "mdi:food"),
        (f"{dog_name}_feeding_snack_count", "Leckerli Anzahl", "mdi:bone"),
        (f"{dog_name}_outside_count", "Draußen Anzahl", "mdi:tree"),
        (f"{dog_name}_walk_count", "Spaziergang Anzahl", "mdi:walk"),
        (f"{dog_name}_play_count", "Spielzeit Anzahl", "mdi:tennis"),
        (f"{dog_name}_training_count", "Training Anzahl", "mdi:school"),
        (f"{dog_name}_poop_count", "Geschäft Anzahl", "mdi:delete"),
        (f"{dog_name}_vet_visits_count", "Tierarztbesuche", "mdi:stethoscope"),
        (f"{dog_name}_medication_count", "Medikamente Anzahl", "mdi:pill"),
        (f"{dog_name}_grooming_count", "Pflege Anzahl", "mdi:shower"),
        (f"{dog_name}_total_vaccinations_count", "Gesamt-Impfungen", "mdi:needle"),
        (f"{dog_name}_rabies_vaccinations_count", "Tollwut-Impfungen", "mdi:needle"),
        (f"{dog_name}_distemper_vaccinations_count", "Staupe-Impfungen", "mdi:needle"),
        (f"{dog_name}_emergency_calls", "Notfälle", "mdi:alert"),
        (f"{dog_name}_missed_feedings", "Verpasste Fütterungen", "mdi:alert"),
        (f"{dog_name}_weekly_activities", "Wöchentliche Aktivitäten", "mdi:calendar-week"),
        (f"{dog_name}_monthly_vet_visits", "Monatliche Tierarztbesuche", "mdi:calendar-month"),
    ]
    for entity_name, friendly_name, icon in counters:
        expected_entities[f"counter.{entity_name}"] = {
            "domain": "counter",
            "friendly_name": f"{dog_name.title()} {friendly_name}",
            "icon": icon,
            "config": {
                "initial": 0,
                "step": 1,
                "minimum": 0,
                "maximum": 999999,
                "icon": icon,
                "restore": True
            }
        }

    # --- Input Select entities ---
    selects = [
        (f"{dog_name}_activity_level", "Aktivitätslevel", ["Sehr niedrig", "Niedrig", "Normal", "Hoch", "Sehr hoch"], "Normal", "mdi:run"),
        (f"{dog_name}_mood", "Stimmung", ["Sehr glücklich", "Glücklich", "Neutral", "Müde", "Gestresst", "Ängstlich", "Unwohl", "Krank"], "Glücklich", "mdi:emoticon-happy"),
        (f"{dog_name}_energy_level_category", "Energie Kategorie", ["Sehr müde", "Müde", "Ruhig", "Normal", "Lebhaft", "Energiegeladen", "Hyperaktiv"], "Normal", "mdi:flash"),
        (f"{dog_name}_appetite_level", "Appetit Level", ["Kein Appetit", "Sehr wenig", "Wenig Appetit", "Normal", "Guter Appetit", "Sehr hungrig", "Gierig"], "Normal", "mdi:food"),
        (f"{dog_name}_health_status", "Gesundheitsstatus", ["Ausgezeichnet", "Sehr gut", "Gut", "Normal", "Leicht unwohl", "Unwohl", "Krank", "Sehr krank", "Notfall"], "Gut", "mdi:heart-pulse"),
        (f"{dog_name}_weather_preference", "Wetterpräferenz", ["Sonnig bevorzugt", "Bewölkt OK", "Leichter Regen OK", "Starker Regen vermeiden", "Schnee OK", "Alle Wetter"], "Sonnig bevorzugt", "mdi:weather-partly-cloudy"),
        (f"{dog_name}_size_category", "Größenkategorie", ["Toy (bis 4kg)", "Klein (4-10kg)", "Mittel (10-25kg)", "Groß (25-40kg)", "Riesig (über 40kg)"], "Mittel (10-25kg)", "mdi:dog"),
        (f"{dog_name}_seasonal_mode", "Saison-Modus", ["Frühling", "Sommer", "Herbst", "Winter", "Automatisch"], "Automatisch", "mdi:leaf"),
        (f"{dog_name}_training_level", "Trainingslevel", ["Untrainiert", "Anfänger", "Grundlagen", "Fortgeschritten", "Gut trainiert", "Experte", "Champion"], "Grundlagen", "mdi:school"),
        (f"{dog_name}_emergency_level", "Notfalllevel", ["Normal", "Beobachten", "Aufmerksamkeit", "Warnung", "Dringend", "Kritisch", "Notfall"], "Normal", "mdi:alert"),
        (f"{dog_name}_vaccination_status", "Impfungsstatus", ["Vollständig geimpft", "Grundimmunisierung abgeschlossen", "Grundimmunisierung läuft", "Auffrischung fällig", "Überfällig", "Noch nicht begonnen"], "Vollständig geimpft", "mdi:needle"),
        (f"{dog_name}_rabies_vaccination_status", "Tollwut-Impfungsstatus", ["Aktuell", "Auffrischung in 6 Monaten", "Auffrischung in 3 Monaten", "Auffrischung in 1 Monat", "Überfällig", "Nie geimpft"], "Aktuell", "mdi:needle"),
        (f"{dog_name}_distemper_vaccination_status", "Staupe-Impfungsstatus", ["Aktuell", "Auffrischung in 6 Monaten", "Auffrischung in 3 Monaten", "Auffrischung in 1 Monat", "Überfällig", "Nie geimpft"], "Aktuell", "mdi:needle"),
        (f"{dog_name}_hepatitis_vaccination_status", "Hepatitis-Impfungsstatus", ["Aktuell", "Auffrischung in 6 Monaten", "Auffrischung in 3 Monaten", "Auffrischung in 1 Monat", "Überfällig", "Nie geimpft"], "Aktuell", "mdi:needle"),
    ]
    for entity_name, friendly_name, options, initial, icon in selects:
        expected_entities[f"input_select.{entity_name}"] = {
            "domain": "input_select",
            "friendly_name": f"{dog_name.title()} {friendly_name}",
            "icon": icon,
            "config": {
                "options": options,
                "initial": initial,
                "icon": icon
            }
        }

    return expected_entities

# =========================
# Entity Creation & Defaults
# =========================

async def _create_missing_entity(hass: HomeAssistant, missing_entity: Dict[str, Any], dog_name: str) -> bool:
    """Create a single missing entity."""
    try:
        entity_id = missing_entity["entity_id"]
        domain = missing_entity["domain"]
        friendly_name = missing_entity["friendly_name"]
        config = missing_entity.get("config", {})
        service_data = {
            "name": friendly_name,
            **config
        }
        await asyncio.wait_for(
            hass.services.async_call(domain, "create", service_data, blocking=True),
            timeout=30.0
        )
        await asyncio.sleep(1.0)
        state = hass.states.get(entity_id)
        if state:
            _LOGGER.debug("Successfully created entity: %s", entity_id)
            return True
        else:
            _LOGGER.warning("Entity created but not found in state registry: %s", entity_id)
            return False
    except asyncio.TimeoutError:
        _LOGGER.error("Timeout creating entity %s", missing_entity["entity_id"])
        return False
    except Exception as e:
        _LOGGER.error("Error creating entity %s: %s", missing_entity["entity_id"], e)
        return False

async def _set_smart_default_values(hass: HomeAssistant, dog_name: str) -> None:
    """Set intelligent default values (e.g. Detmold GPS) for key entities."""
    try:
        # Set default home coordinates (Detmold, Germany)
        home_coords_entity = f"input_text.{dog_name}_home_coordinates"
        if hass.states.get(home_coords_entity):
            state = hass.states.get(home_coords_entity)
            if not state.state or state.state == "":
                await hass.services.async_call(
                    "input_text", "set_value",
                    {
                        "entity_id": home_coords_entity,
                        "value": "52.233333,8.966667"
                    },
                    blocking=True
                )
                _LOGGER.info("🏠 Set default home coordinates for %s to Detmold", dog_name)
        # Set GPS tracker status config
        gps_status_entity = f"input_text.{dog_name}_gps_tracker_status"
        if hass.states.get(gps_status_entity):
            state = hass.states.get(gps_status_entity)
            if not state.state or state.state == "":
                intelligent_config = {
                    "source": "manual",
                    "entity": None,
                    "sensitivity": "medium",
                    "auto_start": False,
                    "auto_end": False,
                    "track_route": True,
                    "calculate_stats": True,
                    "setup_time": None,
                    "status": "ready_for_configuration",
                    "features": {
                        "distance_tracking": True,
                        "speed_calculation": True,
                        "route_recording": True,
                        "geofencing": True,
                        "automatic_detection": False
                    },
                    "thresholds": {
                        "movement_threshold_m": 50,
                        "home_zone_radius_m": 100,
                        "min_walk_duration_min": 5,
                        "max_walk_duration_min": 180
                    }
                }
                await hass.services.async_call(
                    "input_text", "set_value",
                    {
                        "entity_id": gps_status_entity,
                        "value": str(intelligent_config)
                    },
                    blocking=True
                )
                _LOGGER.info("🔧 Set intelligent GPS configuration for %s", dog_name)
        # Set smart default metrics
        smart_defaults = {
            f"input_number.{dog_name}_gps_signal_strength": 100,
            f"input_number.{dog_name}_gps_battery_level": 100,
            f"input_number.{dog_name}_health_score": 8,
            f"input_number.{dog_name}_happiness_score": 8,
            f"input_number.{dog_name}_weight": 15.0,
            f"input_number.{dog_name}_age_years": 3.0,
            f"input_number.{dog_name}_daily_food_amount": 400,
        }
        for entity_id, value in smart_defaults.items():
            if hass.states.get(entity_id):
                state = hass.states.get(entity_id)
                try:
                    if not state.state or float(state.state) == 0:
                        await hass.services.async_call(
                            "input_number", "set_value",
                            {"entity_id": entity_id, "value": value},
                            blocking=True
                        )
                except Exception:
                    pass
        # Set smart select defaults
        select_defaults = {
            f"input_select.{dog_name}_health_status": "Gut",
            f"input_select.{dog_name}_mood": "Glücklich",
            f"input_select.{dog_name}_activity_level": "Normal",
            f"input_select.{dog_name}_size_category": "Mittel (10-25kg)",
        }
        for entity_id, value in select_defaults.items():
            if hass.states.get(entity_id):
                state = hass.states.get(entity_id)
                if not state.state:
                    await hass.services.async_call(
                        "input_select", "select_option",
                        {"entity_id": entity_id, "option": value},
                        blocking=True
                    )
        _LOGGER.info("✅ Smart default values set successfully")
    except Exception as e:
        _LOGGER.warning("⚠️ Error setting smart defaults: %s", e)


