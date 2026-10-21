-- R6 / CONTRACT (SOLO ENTORNO AISLADO con script de QA).
-- ATENCION: romperá servicio Go actual, que usa maintenance.reason.
-- No incluir automaticamente en changelog-master.yaml.
DO $r6$
BEGIN
  IF EXISTS (SELECT 1 FROM training_environment.maintenance
             WHERE reason IS DISTINCT FROM reason_detail) THEN
    RAISE EXCEPTION 'R6: contrato cancelado, existen motivos divergentes';
  END IF;
END;
$r6$;
DROP TRIGGER trg_r6_sync_maintenance_reason ON training_environment.maintenance;
DROP FUNCTION training_environment.fn_r6_sync_maintenance_reason();
ALTER TABLE training_environment.maintenance DROP COLUMN reason;
