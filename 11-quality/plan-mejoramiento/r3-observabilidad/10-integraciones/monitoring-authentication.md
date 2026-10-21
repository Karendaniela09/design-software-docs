# Autenticación de Monitoring

> Estado: En revisión | Última actualización: 2026-10-20
> Autor: Kevin Andrey Culma Gómez | Equipo: Monitoring / ADSO 3145555

> Documento trasladado desde la entrega original. Las rutas de capturas y salidas se consultan en la carpeta local `EVIDENCIAS-PLAN-MEJORAMIENTO-R3`. Para el corte vigente, consultar el índice R3 y `estado-actual.md`; los resultados antiguos conservan su fecha y alcance.

La API verifica JWT RS256 con `JWKS_URL`, `JWT_ISSUER` y `JWT_AUDIENCE`; el perfil local con IAM verifica sus tokens reales. La identidad aislada R3 permite pruebas separadas con `JWT_PUBLIC_KEY_FILE`. Sin configuración, la autenticación falla cerrada. El IdP institucional permanece sin validar por falta de acceso.
