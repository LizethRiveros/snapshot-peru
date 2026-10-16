# snapshot-peru

Historia versionada y gratuita de series clave de la economía peruana.
Cada día un workflow descarga las series, las guarda como CSV y hace commit **solo si algo cambió**.
Con `git log` y `git diff` ves cuándo cambió un dato, incluidas las **revisiones** que hace la fuente.

## Series (BCRP, vía BCRPData)

Ver [`data/catalogo.json`](data/catalogo.json) para la lista, la última fecha y el último valor.
Los CSV están en `data/bcrp/`: columnas `fecha` (ISO), `valor` (vacío = sin dato / día no hábil) y `periodo_fuente` (etiqueta original).

Para agregar una serie, añádela a [`series.json`](series.json) (el código sale del catálogo de BCRPData).

## Uso

```bash
python scripts/snapshot.py            # solo librería estándar, Python 3.9+
git log -p -- data/bcrp/inflacion-lima-12m.csv   # historia de una serie
```

## Fuentes y alcance

- **BCRP**: API pública BCRPData. No es un proyecto oficial ni está afiliado al BCRP.
- **INEI**: las series de IPC, empleo y precios cuya fuente original es el INEI entran vía BCRPData (que las republica). Los microdatos de encuestas del INEI no son series y no se incluyen.
- **SBS**: su portal bloquea consultas automáticas y no se intenta evadirlo; el tipo de cambio ya está en las series del BCRP.
- Datos referenciales; verifique en la fuente oficial antes de decidir.
