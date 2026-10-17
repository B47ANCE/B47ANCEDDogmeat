"""Validate proposal consistency only; never execute a dog/controller/database."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def check():
    errors = []
    data = json.loads((ROOT / 'docs/contracts/database_redesign.json').read_text(encoding='utf-8'))
    version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    if data.get('project_version') != version or data.get('status') != 'DESIGN_ONLY_NOT_IMPLEMENTED':
        errors.append('Design version/status differs')
    for key, value in {'runtime_enabled': False, 'native_no_go_retained': True,
                       'sqlite_verified': False, 'safe_store_mode_verified': False,
                       'primary_owner_unique': True, 'secondary_bond_can_transfer_ownership': False,
                       'trust_alone_grants_permission': False, 'arbitrary_claim_button': False,
                       'leases_survive_restart': False, 'owner_reconnect_teleports': False,
                       'owner_reconnect_preempts_without_command': False,
                       'store_offline_enabled': False}.items():
        if data.get(key) is not value:
            errors.append('Design boundary changed without reviewed capability: ' + key)
    for key in ('max_active_leases_per_dog', 'max_active_tasks_per_dog', 'max_physical_movement_writers'):
        if type(data.get(key)) is not int or data[key] != 1:
            errors.append('Single authority invariant differs: ' + key)
    if data['canonical_key'] != ['worldId', 'dogId'] or data['relationship_key'] != ['worldId', 'dogId', 'principalId']:
        errors.append('Canonical/relationship keys differ')
    principal = data['principal_policy']
    if (principal['source'] != 'AUTHENTICATED_SERVER_CONNECTION'
            or principal['steamid_encoding'] != 'DECIMAL_STRING_NEVER_LUA_NUMBER'
            or principal['client_identity_accepted'] is not False):
        errors.append('Unsafe principal design')
    if data['bond_range'] != {'minimum': 0, 'maximum': 100, 'primary_completion': 100}:
        errors.append('Primary bond requirements differ')
    groups = data['field_groups']
    if set(groups) != {'identity', 'geneticsAppearance', 'personality', 'training', 'health',
                       'welfare', 'equipmentInventory', 'homeWorld', 'persistence'}:
        errors.append('Missing canine record category')
    for group, fields in groups.items():
        if not fields or len(fields) != len(set(fields)) or any(not isinstance(f, str) or not f for f in fields):
            errors.append('Invalid/duplicate design fields: ' + group)
    for key in ('relationship_fields', 'lease_fields', 'task_definition_fields', 'durable_task_fields'):
        if not data[key] or len(data[key]) != len(set(data[key])):
            errors.append('Incomplete/duplicate field index: ' + key)
    collections = data['entity_collections']
    if set(collections) != {'dogs', 'relationships', 'primaryOwners', 'tasks', 'resourceClaims',
                            'interactionReceipts', 'completionReceipts', 'lifecycleIntents',
                            'terminalTombstones', 'cosmeticEntitlements', 'checkpoints'}:
        errors.append('Missing logical collection/transaction index')
    if data['active_task_states'] != ['Assigned', 'Running']:
        errors.append('Active task slot semantics differ')
    states = data['task_states']
    if set(states) != {'Requested', 'Validated', 'Assigned', 'Running', 'Suspended', 'Completed', 'Cancelled', 'Failed'}:
        errors.append('Public task state vocabulary differs')
    transitions = data['task_transitions']
    terminal = set(data['task_terminal_states'])
    for source, target in transitions:
        if source not in states or target not in states or source in terminal or source == target:
            errors.append('Invalid or resurrecting task transition')
    if len({tuple(t) for t in transitions}) != len(transitions):
        errors.append('Duplicate task transition')
    if [x['priority'] for x in data['priorities']] != list(range(1, 8)) or [x['category'] for x in data['priorities']] != [
            'ImmediateSurvival', 'UrgentBiologicalNeeds', 'PrimaryOwner', 'TrustedHandler',
            'AutonomousCare', 'NonurgentAssignedWork', 'SocialIdle']:
        errors.append('Latest task priority order differs')
    if set(data['dog_lifecycle_states']) != {'WILD', 'BONDING', 'OWNED_ACTIVE', 'OWNER_OFFLINE_SELFCARE',
                                            'WITHDRAW_PENDING', 'STORED_OFFLINE', 'RESTORE_PENDING',
                                            'QUARANTINED', 'DECEASED'}:
        errors.append('Lifecycle vocabulary differs')
    for key, expected in {'real_resources_only': True, 'automatic_respawn': False,
                          'copied_marker_authorizes': False, 'missing_body_means_stored': False,
                          'serious_conditions_auto_cure': False, 'proximity_training_xp': False,
                          'death_terminal': True, 'native_private_atomicity_proven': False}.items():
        if data['physical_invariants'].get(key) is not expected:
            errors.append('Physical invariant differs: ' + key)
    settings = data['sandbox_settings']
    expected = {'OfflineCompanionMode', 'OfflineSafehouseRestriction', 'OfflineDoghouseGrowth',
                'AllowTrustedOfflineCaretakers', 'AllowTrustedOfflineTraining'}
    if {s['id'] for s in settings} != {'B47ANCEDDogmeat.' + name for name in expected} or len(settings) != 5:
        errors.append('Setting proposal identifiers differ')
    for setting in settings:
        if setting['server_authority'] is not True or setting['status'] != 'PROPOSAL_NOT_REGISTERED':
            errors.append('Setting authority/availability overclaim')
        if not setting['existing_save_policy'] or not setting['capability_gates']:
            errors.append('Missing setting recovery/gates')
        if setting['type'] == 'enum':
            if (setting['allowed_values'] != ['SelfCare', 'StoreOffline'] or setting['default'] != 'SelfCare'
                    or setting['engine_default'] != 1 or setting['engine_num_values'] != 2):
                errors.append('Offline mode mapping/default differs')
        elif setting['type'] != 'boolean' or setting['default'] is not True:
            errors.append('Boolean proposal/default differs')
        for key in ('name_key', 'tooltip_key'):
            if setting[key] not in data['english_fallback']:
                errors.append('Missing proposed option label')
    if data['offline_default'] != 'SelfCare':
        errors.append('Approved offline default differs')
    scenarios = data['task_acceptance']
    if [s['id'] for s in scenarios] != [f'TA{i:02}' for i in range(1, 19)]:
        errors.append('Missing/duplicate required task acceptance case')
    for case in scenarios:
        if case['status'] != 'BLOCKED / NOT TESTED' or not case['scenario'] or not case['required']:
            errors.append('Acceptance overclaim/incomplete scenario')
    for request in data['source_requests']:
        relative = Path(request['path'])
        if relative.is_absolute() or '..' in relative.parts or not request['path'].startswith('docs/requirements/'):
            errors.append('Unsafe request snapshot path')
        elif hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != request['sha256']:
            errors.append('Supplied request snapshot bytes changed')
    return errors


def main():
    errors = check()
    print(json.dumps({'status': 'STATIC DESIGN PASS' if not errors else 'FAIL',
                      'project_version': (ROOT / 'VERSION').read_text(encoding='utf-8').strip(),
                      'dog_field_categories': 9, 'proposed_settings': 5, 'required_task_scenarios': 18,
                      'evidence': 'Structural consistency only; no gameplay/database/controller execution',
                      'runtime_implementation': 'NOT IMPLEMENTED', 'G6': 'NOT TESTED',
                      'G7': 'BLOCKED / NOT TESTED', 'G8': 'BLOCKED', 'errors': errors}, indent=2))
    return bool(errors)


if __name__ == '__main__':
    sys.exit(main())
