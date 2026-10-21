DO $r6$ BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns
       WHERE table_schema='training_environment' AND table_name='maintenance'
         AND column_name='reason') THEN
    RAISE EXCEPTION 'R6/C1: vieja columna reason aun presente';
  END IF;
  IF (SELECT reason_detail FROM training_environment.maintenance
        WHERE id='00000000-0000-4000-8000-000000000617') <> 'Cambio desde v2' THEN
    RAISE EXCEPTION 'R6/C1: motivo perdido durante CONTRACT';
  END IF;
END $r6$;
-- Solamente compatible con un consumidor que ya use reason_detail.
UPDATE training_environment.maintenance SET reason_detail='Solo v2 despues de CONTRACT'
  WHERE id='00000000-0000-4000-8000-000000000617';
SELECT 'R6 CONTRACT aislado OK' AS result;
