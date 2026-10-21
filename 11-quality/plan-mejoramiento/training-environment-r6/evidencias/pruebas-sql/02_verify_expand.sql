-- A: backfill de datos historicos.
DO $r6$ BEGIN
  IF EXISTS (SELECT 1 FROM training_environment.maintenance
             WHERE reason IS DISTINCT FROM reason_detail) THEN
    RAISE EXCEPTION 'R6/E1: backfill incompleto';
  END IF;
  IF (SELECT reason_detail FROM training_environment.maintenance
      WHERE id='00000000-0000-4000-8000-000000000613') <> 'Inspeccion pre-R6' THEN
    RAISE EXCEPTION 'R6/E1: la fila historica perdio datos';
  END IF;
END $r6$;
-- B: el consumidor antiguo sigue escribiendo reason.
INSERT INTO training_environment.maintenance
  (id, environment_id, start_date, end_date, start_time, end_time, reason, created_by)
VALUES ('00000000-0000-4000-8000-000000000616','00000000-0000-4000-8000-000000000611',
  '2026-11-05','2026-11-06','08:00','09:00','Escritura API v1',
  '00000000-0000-4000-8000-000000000614');
-- C: cliente futuro utiliza reason_detail.
INSERT INTO training_environment.maintenance
  (id, environment_id, start_date, end_date, start_time, end_time, reason_detail, created_by)
VALUES ('00000000-0000-4000-8000-000000000617','00000000-0000-4000-8000-000000000611',
  '2026-11-07','2026-11-08','08:00','09:00','Escritura API v2',
  '00000000-0000-4000-8000-000000000614');
-- D: UPDATE de ambos consumidores, preservando sincronizacion.
UPDATE training_environment.maintenance SET reason='Cambio desde v1'
  WHERE id='00000000-0000-4000-8000-000000000616';
UPDATE training_environment.maintenance SET reason_detail='Cambio desde v2'
  WHERE id='00000000-0000-4000-8000-000000000617';
DO $r6$ BEGIN
  IF EXISTS (SELECT 1 FROM training_environment.maintenance
             WHERE reason IS DISTINCT FROM reason_detail) THEN
    RAISE EXCEPTION 'R6/E2: el trigger no sincroniza ambas escrituras';
  END IF;
  IF (SELECT reason FROM training_environment.maintenance
      WHERE id='00000000-0000-4000-8000-000000000617') <> 'Cambio desde v2' THEN
    RAISE EXCEPTION 'R6/E2: escritura v2 no visible por cliente v1';
  END IF;
  -- E: conflicto simultaneo se rechaza de manera explicita.
  BEGIN
    INSERT INTO training_environment.maintenance
      (id, environment_id, start_date, end_date, reason, reason_detail, created_by)
    VALUES ('00000000-0000-4000-8000-000000000618',
      '00000000-0000-4000-8000-000000000611','2026-11-09','2026-11-10',
      'distinto A','distinto B','00000000-0000-4000-8000-000000000614');
    RAISE EXCEPTION 'R6/E3: una escritura contradictoria fue aceptada';
  EXCEPTION WHEN check_violation THEN
    NULL; -- esperado de nuestra funcion antes de la insercion
  END;
  IF EXISTS (SELECT 1 FROM training_environment.maintenance
             WHERE id='00000000-0000-4000-8000-000000000618') THEN
    RAISE EXCEPTION 'R6/E3: se guardo fila contradictoria';
  END IF;
END $r6$;
SELECT 'R6 E1-E3 OK (backfill + v1/v2 + divergencia)' AS result;
