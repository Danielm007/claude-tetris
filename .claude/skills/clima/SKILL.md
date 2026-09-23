---
name: clima
description: Consulta el clima actual y el pronóstico de los próximos días para la ubicación local del usuario (detectada por IP) o para una ciudad indicada. Úsalo cuando el usuario pregunte por el clima, el tiempo, la temperatura, si va a llover, o invoque /clima.
argument-hint: "[ciudad opcional, p. ej. Quito]"
allowed-tools: Bash(python3 .claude/skills/clima/clima.py*), Bash(python3 */.claude/skills/clima/clima.py*)
---

# Clima

Obtiene el clima usando APIs públicas sin clave:

- **Ubicación local:** se detecta por IP con `ipapi.co` (respaldo: `ip-api.com`).
- **Ciudad indicada:** se geocodifica con la API de geocoding de Open-Meteo.
- **Datos del clima:** `api.open-meteo.com` (actual + pronóstico de 3 días).

## Cómo usarlo

1. Si el usuario indicó una ciudad (en `$ARGUMENTS` o en su mensaje), pásala como argumento. Si no, ejecútalo sin argumentos para usar la ubicación local.

   ```bash
   python3 .claude/skills/clima/clima.py            # ubicación local
   python3 .claude/skills/clima/clima.py "Quito"    # ciudad concreta
   ```

2. El script imprime JSON con `ubicacion`, `actual` y `pronostico`. Resume la respuesta en español, de forma breve:
   - Ubicación (ciudad, país) y si se detectó por IP.
   - Condición actual, temperatura, sensación térmica, humedad y viento.
   - Pronóstico de los próximos días: máx/mín, condición y probabilidad de lluvia.
   - Si el usuario preguntó algo concreto (p. ej. "¿necesito paraguas?"), respóndelo directamente con esos datos.

3. Si el script devuelve un campo `error`, explícalo al usuario y sugiere indicar la ciudad manualmente (la detección por IP puede fallar con VPN o sin conexión).

## Notas

- La ubicación por IP es aproximada (nivel ciudad) y puede reflejar la del proveedor o la VPN.
- Unidades: °C, km/h, mm. Zona horaria automática según la ubicación.
