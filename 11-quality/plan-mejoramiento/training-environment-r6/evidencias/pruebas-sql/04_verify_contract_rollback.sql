DO $r6$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns
       WHERE table_schema='training_environment' AND table_name='maintenance'
         AND column_name='reason') THEN
    RAISE EXCEPTION 'R6/C2: rollback no restauro reason';
  END IF;
  IF EXISTS (SELECT 1 FROM training_environment.maintenance
       WHERE reason IS DISTINCT FROM reason_detail) THEN
    RAISE EXCEPTION 'R6/C2: rollback contrato dejo valores divergentes';
  END IF;
  IF (SELECT reason FROM training_environment.maintenance
      WHERE id='00000000-0000-4000-8000-000000000617') <> 'Solo v2 despues de CONTRACT' THEN
    RAISE EXCEPTION 'R6/C2: rollback perdio escritura realizada en contrato';
  END IF;
END $r6$;
SELECT 'R6 rollback CONTRACT OK (datos preservados)' AS result;
