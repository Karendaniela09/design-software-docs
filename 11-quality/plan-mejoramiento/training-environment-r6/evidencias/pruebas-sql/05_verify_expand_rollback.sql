DO $r6$ BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns
       WHERE table_schema='training_environment' AND table_name='maintenance'
         AND column_name='reason_detail') THEN
    RAISE EXCEPTION 'R6/RB: reason_detail no se elimino al revertir';
  END IF;
  IF (SELECT reason FROM training_environment.maintenance
      WHERE id='00000000-0000-4000-8000-000000000617') <> 'Solo v2 despues de CONTRACT' THEN
    RAISE EXCEPTION 'R6/RB: perdio datos nuevos tras rollback completo';
  END IF;
  IF (SELECT reason FROM training_environment.maintenance
      WHERE id='00000000-0000-4000-8000-000000000613') <> 'Inspeccion pre-R6' THEN
    RAISE EXCEPTION 'R6/RB: perdio dato historico';
  END IF;
END $r6$;
SELECT 'R6 E4 OK: rollback expand/backfill, datos conservados' AS result;
