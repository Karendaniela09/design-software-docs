-- El rollback recupera reason a partir de reason_detail, SIN truncar datos
-- ya que ambos son VARCHAR(255). Reinstala sincronizacion dual.
ALTER TABLE training_environment.maintenance ADD COLUMN reason VARCHAR(255);
UPDATE training_environment.maintenance SET reason = reason_detail;
