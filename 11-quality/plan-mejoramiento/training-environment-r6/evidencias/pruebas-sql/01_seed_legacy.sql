-- Datos cargados ANTES del expand: una fila con motivo, otra con NULL.
-- Evitamos depender de los seeds de desarrollo del resto del proyecto.
INSERT INTO training_environment.environment_type(id, name, code)
  VALUES ('00000000-0000-4000-8000-000000000610', 'R6 Tipo local', 'R6_LOCAL')
  ON CONFLICT (id) DO NOTHING;
INSERT INTO training_environment.environment(id, environment_type_id, training_center_id, name, capacity, location)
  VALUES ('00000000-0000-4000-8000-000000000611',
          '00000000-0000-4000-8000-000000000610',
          '00000000-0000-4000-8000-000000000612', 'R6 ambiente aislado', 15, 'Laboratorio de QA')
  ON CONFLICT (id) DO NOTHING;
INSERT INTO training_environment.maintenance
  (id, environment_id, start_date, end_date, start_time, end_time, reason, created_by)
  VALUES ('00000000-0000-4000-8000-000000000613', '00000000-0000-4000-8000-000000000611',
   '2026-11-01','2026-11-02','08:00','09:00','Inspeccion pre-R6', '00000000-0000-4000-8000-000000000614'),
   ('00000000-0000-4000-8000-000000000615','00000000-0000-4000-8000-000000000611',
   '2026-11-03','2026-11-04','08:00','09:00',NULL,'00000000-0000-4000-8000-000000000614');
DO $r6$ BEGIN
  IF (SELECT COUNT(*) FROM training_environment.maintenance
      WHERE environment_id='00000000-0000-4000-8000-000000000611') <> 2 THEN
    RAISE EXCEPTION 'R6: faltan fixtures pre-expand';
  END IF;
END $r6$;
