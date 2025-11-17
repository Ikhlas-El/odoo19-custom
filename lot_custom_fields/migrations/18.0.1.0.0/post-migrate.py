import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Post-migration script to migrate old selection values to new Many2one records
    """
    _logger.info("Starting post-migration: Migrating x_origine data")

    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})

    # Mapping of old selection values to new origin records
    origins_mapping = {
        'Col': 'coffee_origin_colombie',
        'Vit': 'coffee_origin_vietnam',
        'ETH': 'coffee_origin_ethiopie',
        'Ugh': 'coffee_origin_ouganda',
        'Ind': 'coffee_origin_inde',
    }

    # Get all lots with legacy data
    cr.execute("""
        SELECT id, x_origine_legacy 
        FROM stock_lot 
        WHERE x_origine_legacy IS NOT NULL
    """)

    lots_to_migrate = cr.fetchall()
    _logger.info(f"Found {len(lots_to_migrate)} lots to migrate")

    migrated_count = 0
    error_count = 0

    for lot_id, old_value in lots_to_migrate:
        if old_value in origins_mapping:
            try:
                # Get the new origin record
                origin_xml_id = f"your_module.{origins_mapping[old_value]}"
                origin = env.ref(origin_xml_id, raise_if_not_found=False)

                if origin:
                    # Update the lot with new Many2one value
                    cr.execute("""
                        UPDATE stock_lot 
                        SET x_origine = %s 
                        WHERE id = %s
                    """, (origin.id, lot_id))
                    migrated_count += 1
                else:
                    _logger.warning(f"Origin record not found for XML ID: {origin_xml_id}")
                    error_count += 1
            except Exception as e:
                _logger.error(f"Error migrating lot {lot_id}: {str(e)}")
                error_count += 1
        else:
            _logger.warning(f"Unknown origin value '{old_value}' for lot {lot_id}")
            error_count += 1

    cr.commit()

    _logger.info(f"Post-migration completed: {migrated_count} lots migrated successfully, {error_count} errors")

    # Optional: Remove the legacy field after successful migration
    # Uncomment the following lines after verifying migration was successful
    # cr.execute("ALTER TABLE stock_lot DROP COLUMN IF EXISTS x_origine_legacy")
    # cr.commit()
    # _logger.info("Removed x_origine_legacy column")