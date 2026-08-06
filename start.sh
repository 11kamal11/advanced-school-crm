#!/bin/bash
# Launches this project's own Odoo instance (port 8071), fully separate
# from the shared system service on :8070.
cd "$(dirname "$0")"
exec /usr/bin/odoo --config conf/odoo-school-crm.conf "$@"
