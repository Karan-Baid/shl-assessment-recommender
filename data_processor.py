import json
from typing import List, Dict
import config

def load_catalog(filename: str = None) -> List[Dict]:
    if filename is None:
        filename = config.CATALOG_FILE

    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_rich_text(assessment: Dict) -> str:
    parts = []

    if assessment.get('name'):
        parts.append(f"Assessment: {assessment['name']}")

    if assessment.get('description'):
        parts.append(f"Description: {assessment['description']}")

    if assessment.get('test_type'):
        test_type_full = config.TEST_TYPES.get(assessment['test_type'], 'Unknown')
        parts.append(f"Type: {test_type_full}")

    if assessment.get('duration'):
        parts.append(f"Duration: {assessment['duration']}")

    if assessment.get('category'):
        parts.append(f"Category: {assessment['category']}")

    if assessment.get('skills'):
        skills_str = ', '.join(assessment['skills'])
        parts.append(f"Skills: {skills_str}")

    return ' | '.join(parts)

def normalize_assessment(assessment: Dict) -> Dict:
    normalized = {
        'url': assessment.get('url', ''),
        'name': assessment.get('name', 'Unknown Assessment'),
        'description': assessment.get('description', '')[:500],
        'test_type': assessment.get('test_type', 'K'),
        'category': assessment.get('category', ''),
        'duration': assessment.get('duration', ''),
        'skills': assessment.get('skills', []),
        'search_text': ''
    }

    normalized['search_text'] = create_rich_text(normalized)

    return normalized

def process_catalog(assessments: List[Dict]) -> List[Dict]:
    print(f"Processing {len(assessments)} assessments...")

    processed = []
    for assessment in assessments:
        try:
            normalized = normalize_assessment(assessment)
            if normalized['url'] and normalized['name']:
                processed.append(normalized)
        except Exception as e:
            print(f"Error processing assessment: {e}")
            continue

    print(f"Successfully processed {len(processed)} assessments")
    return processed

def save_processed_catalog(assessments: List[Dict], filename: str = None):
    if filename is None:
        filename = config.CATALOG_FILE.replace('.json', '_processed.json')

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(assessments, f, indent=2, ensure_ascii=False)

    print(f"Saved processed catalog to {filename}")

def get_search_texts(assessments: List[Dict]) -> List[str]:
    return [a['search_text'] for a in assessments]

def main():

    catalog = load_catalog()
    print(f"Loaded {len(catalog)} assessments from catalog")

    processed = process_catalog(catalog)

    save_processed_catalog(processed)

    print("\nProcessed Catalog Statistics:")
    print(f"  Total assessments: {len(processed)}")

    test_types = {}
    for a in processed:
        tt = a.get('test_type', 'Unknown')
        test_types[tt] = test_types.get(tt, 0) + 1

    print("\n  Test type distribution:")
    for tt, count in sorted(test_types.items()):
        print(f"    {tt} ({config.TEST_TYPES.get(tt, 'Unknown')}): {count}")

    print("\nSample processed assessment:")
    if processed:
        sample = processed[0]
        print(f"  Name: {sample['name']}")
        print(f"  URL: {sample['url']}")
        print(f"  Type: {sample['test_type']}")
        print(f"  Search text (truncated): {sample['search_text'][:200]}...")

if __name__ == "__main__":
    main()
