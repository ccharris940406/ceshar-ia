# Chequeador

An Odoo module developed by **Desoft** for managing mining truck dispatch operations (Moanickel project). It extends Odoo's Fleet module to track trucks, loading origins, unloading destinations, and mineral types.

## Features

- **Truck management** — extends `fleet.vehicle` with a radio number field for field communication.
- **Truck model capacity** — extends `fleet.vehicle.model` with a load capacity (tonnage) field.
- **Mining origins** — define extraction points with cycle time and associated mineral type.
- **Destinations** — define unloading points categorized by destination type.
- **Minerals catalog** — maintain a catalog of mined mineral types.

## Module Structure

```
chequeador/
├── models/
│   ├── chequeador_camion.py          # Extends fleet.vehicle (adds radio number)
│   ├── chequeador_camion_modelo.py   # Extends fleet.vehicle.model (adds load capacity)
│   ├── chequeador_origen.py          # Mining origin model
│   ├── chequeador_destino.py         # Unloading destination model
│   ├── chequeador_destino_tipo.py    # Destination type catalog
│   └── chequeador_minerales.py       # Minerals catalog
├── views/
│   ├── chequeador_camion.xml
│   ├── chequeador_camion_modelo_view.xml
│   ├── chequeador_destino_views.xml
│   └── chequeador_origen_views.xml
├── data/
│   └── chequeador_menu.xml
├── security/
│   └── ir.model.access.csv
└── __manifest__.py
```

## Dependencies

| Module | Purpose |
|--------|---------|
| `base`  | Core Odoo framework |
| `fleet` | Vehicle and fleet management |

## Installation

1. Copy the `chequeador` folder into your Odoo `addons` directory.
2. Restart the Odoo server.
3. Enable **Developer Mode** (Settings → Activate the developer mode).
4. Go to **Apps**, click **Update Apps List**, then search for **Chequeador** and install it.

## Access Rights

All models grant full CRUD permissions (`read`, `write`, `create`, `unlink`) to the base internal user group (`base.group_user`).

## Authors

Developed by **Desoft** for the **Moanickel** project.
