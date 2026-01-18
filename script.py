import json
import re
import subprocess
import shutil
from pathlib import Path
from typing import Any, Dict


ERD_INPUT = r"""
```json\n{\n  \"tables\": {\n    \"Hospital\": {\n      \"*hospital_id\": \"int() NOT NULL\",\n      \"name\": \"varchar(100) NOT NULL\",\n      \"address\": \"varchar(200) NOT NULL\"\n    },\n    \"Department\": {\n      \"*department_id\": \"int() NOT NULL\",\n      \"+hospital_id\": \"int()\",\n      \"name\": \"varchar(100) NOT NULL\",\n      \"coordinator\": \"varchar(100) NOT NULL\"\n    },\n    \"Person\": {\n      \"*person_id\": \"int() NOT NULL\",\n      \"full_name\": \"varchar(100) NOT NULL\",\n      \"cpf\": \"varchar(11) NOT NULL\",\n      \"rg\": \"varchar(10) NOT NULL\",\n      \"date_of_birth\": \"date() NOT NULL\",\n      \"address\": \"varchar(200) NOT NULL\"\n    },\n    \"Employee\": {\n      \"*employee_id\": \"int() NOT NULL\",\n      \"+person_id\": \"int()\",\n      \"professional_credentials\": \"varchar(100) NOT NULL\",\n      \"role\": \"varchar(50) NOT NULL\"\n    },\n    \"Patient\": {\n      \"*patient_id\": \"int() NOT NULL\",\n      \"+person_id\": \"int()\",\n      \"identification_wristband\": \"varchar(20) NOT NULL\",\n      \"status\": \"varchar(20) NOT NULL\"\n    },\n    \"Visitor\": {\n      \"*visitor_id\": \"int() NOT NULL\",\n      \"+person_id\": \"int()\",\n      \"type\": \"varchar(20) NOT NULL\",\n      \"identification_card\": \"varchar(20) NOT NULL\"\n    },\n    \"Address\": {\n      \"*address_id\": \"int() NOT NULL\",\n      \"+person_id\": \"int()\",\n      \"address\": \"varchar(200) NOT NULL\",\n      \"last_update\": \"timestamp() NOT NULL\"\n    },\n    \"IdentificationCard\": {\n      \"*identification_card_id\": \"int() NOT NULL\",\n      \"+employee_id\": \"int()\",\n      \"issue_date\": \"date() NOT NULL\",\n      \"expiry_date\": \"date() NOT NULL\",\n      \"access_level\": \"varchar(10) NOT NULL\"\n    },\n    \"EmployeeSchedule\": {\n      \"*employee_schedule_id\": \"int() NOT NULL\",\n      \"+employee_id\": \"int()\",\n      \"work_pattern\": \"varchar(20) NOT NULL\",\n      \"schedule\": \"varchar(50) NOT NULL\"\n    },\n    \"TimeClockRecord\": {\n      \"*time_clock_record_id\": \"int() NOT NULL\",\n      \"+employee_id\": \"int()\",\n      \"clock_in\": \"timestamp() NOT NULL\",\n      \"clock_out\": \"timestamp() NOT NULL\"\n    },\n    \"WorkShift\": {\n      \"*work_shift_id\": \"int() NOT NULL\",\n      \"+employee_id\": \"int()\",\n      \"start_time\": \"time() NOT NULL\",\n      \"end_time\": \"time() NOT NULL\"\n    },\n    \"AvailabilityException\": {\n      \"*availability_exception_id\": \"int() NOT NULL\",\n      \"+employee_id\": \"int()\",\n      \"start_date\": \"date() NOT NULL\",\n      \"end_date\": \"date() NOT NULL\",\n      \"type\": \"varchar(20) NOT NULL\",\n      \"note\": \"text()\"\n    },\n    \"DepartmentOccupancy\": {\n      \"*department_occupancy_id\": \"int() NOT NULL\",\n      \"+department_id\": \"int()\",\n      \"occupancy\": \"int() NOT NULL\",\n      \"capacity\": \"int() NOT NULL\"\n    }\n  },\n  \"relations\": [\n    \"Hospital:hospital_id 1--* Department:hospital_id\",\n    \"Department:department_id 1--* Employee:department_id\",\n    \"Person:person_id 1--* Employee:person_id\",\n    \"Person:person_id 1--* Patient:person_id\",\n    \"Person:person_id 1--* Visitor:person_id\",\n    \"Person:person_id 1--* Address:person_id\",\n    \"Employee:employee_id 1--* IdentificationCard:employee_id\",\n    \"Employee:employee_id 1--* EmployeeSchedule:employee_id\",\n    \"Employee:employee_id 1--* TimeClockRecord:employee_id\",\n    \"Employee:employee_id 1--* WorkShift:employee_id\",\n    \"Employee:employee_id 1--* AvailabilityException:employee_id\",\n    \"Department:department_id 1--* DepartmentOccupancy:department_id\"\n  ],\n  \"rankAdjustments\": [],\n  \"label\": \"Integrated Hospital Management System\"\n}\n```
"""

OUT_DIR = Path("output")
BASE_NAME = "hospital_erd" 

def ensure_cmd(cmd: str) -> None:
    """Verifica se um comando existe no PATH do sistema."""
    if shutil.which(cmd) is None:
        raise SystemExit(f"Comando '{cmd}' não encontrado no PATH. Instale/ajuste o PATH e tente de novo.")

def parse_messy_json(input_text: str) -> Dict[str, Any]:
    """
    Limpa e converte strings JSON "sujas" ou formatadas como markdown.
    """
    if not isinstance(input_text, str) or not input_text.strip():
        raise ValueError("Entrada vazia ou inválida.")

    t = input_text.strip()

    if (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
        try:
            decoded = json.loads(t)
            if isinstance(decoded, dict):
                return decoded
            if isinstance(decoded, str):
                t = decoded.strip()
            else:
                t = str(decoded).strip()
        except Exception:
            # Se falhar o load direto, remove as aspas das pontas manualmente
            t = t[1:-1].strip()

    # Se tiver bloco ```...```, pega o conteúdo interno usando Regex
    #    Isso resolve o problema da string vir com "```json"
    m = re.search(r"```(?:json)?\s*(.*?)\s*```", t, flags=re.DOTALL | re.IGNORECASE)
    if m:
        t = m.group(1).strip()

    # Se ainda tiver escapes literais (\n, \"), tenta “desescapar”
    if "\\n" in t or '\\"' in t or "\\t" in t:
        try:
            t2 = json.loads(f'"{t}"')
            if isinstance(t2, str):
                t = t2.strip()
        except Exception:
            pass

    # Recorta do primeiro { ao último } pra ignorar lixo ao redor
    first = t.find("{")
    last = t.rfind("}")
    if first != -1 and last != -1 and last > first:
        t = t[first:last + 1].strip()

    return json.loads(t)

def normalize_erdot_json(data: Dict[str, Any]) -> Dict[str, Any]:
    # Normaliza os dados para o formato esperado pelo ERDot.
    ra = data.get("rankAdjustments", "")
    if isinstance(ra, list):
        data["rankAdjustments"] = "\n".join(str(x) for x in ra)
    elif ra is None:
        data["rankAdjustments"] = ""
    elif not isinstance(ra, str):
        data["rankAdjustments"] = str(ra)

    if "tables" not in data or not isinstance(data["tables"], dict):
        data["tables"] = {}
    if "relations" not in data or not isinstance(data["relations"], list):
        data["relations"] = []
    if "label" not in data or not isinstance(data["label"], str):
        data["label"] = str(data.get("label", ""))

    return data

def main() -> None:
    # Verifica dependências externas
    ensure_cmd("erdot")
    ensure_cmd("dot")

    # Cria diretório de saída
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("--- Iniciando Processamento ---")
    
    # Processa o JSON
    try:
        data = parse_messy_json(ERD_INPUT)
        data = normalize_erdot_json(data)
    except Exception as e:
        print(f"Erro ao processar o JSON de entrada: {e}")
        return

    # Define caminhos dos arquivos
    json_path = OUT_DIR / f"{BASE_NAME}.erd.json"
    dot_path = OUT_DIR / f"{BASE_NAME}.dot"
    png_path = OUT_DIR / f"{BASE_NAME}.png"
    svg_path = OUT_DIR / f"{BASE_NAME}.svg"

    # Salva o JSON limpo
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"JSON limpo salvo em: {json_path}")

    # JSON -> DOT (ERDot)
    print("Gerando arquivo .dot...")
    subprocess.run(["erdot", str(json_path), "-o", str(dot_path)], check=True)

    # DOT -> Imagens (Graphviz)
    print("Renderizando imagens (PNG e SVG)...")
    subprocess.run(["dot", str(dot_path), "-Tpng", "-o", str(png_path)], check=True)
    subprocess.run(["dot", str(dot_path), "-Tsvg", "-o", str(svg_path)], check=True)

    print("\n Sucesso! Arquivos gerados:")
    print(f"   -> {png_path}")
    print(f"   -> {svg_path}")

if __name__ == "__main__":
    main()