-- DDL para el sistema transaccional origen FinBank S.A.

CREATE TABLE IF NOT EXISTS TB_CLIENTES_CORE (
    id_cli INTEGER PRIMARY KEY,
    nomb_cli TEXT NOT NULL,
    apell_cli TEXT NOT NULL,
    tip_doc TEXT NOT NULL,
    num_doc TEXT NOT NULL,
    fec_nac TEXT,
    fec_alta TEXT,
    cod_segmento TEXT,
    score_buro INTEGER,
    ciudad_res TEXT,
    depto_res TEXT,
    estado_cli TEXT,
    canal_adquis TEXT
);

CREATE TABLE IF NOT EXISTS TB_PRODUCTOS_CAT (
    cod_prod TEXT PRIMARY KEY,
    desc_prod TEXT NOT NULL,
    tip_prod TEXT NOT NULL,
    tasa_ea REAL,
    plazo_max_meses INTEGER,
    cuota_min REAL,
    comision_admin REAL,
    estado_prod TEXT
);

CREATE TABLE IF NOT EXISTS TB_SUCURSALES_RED (
    cod_suc TEXT PRIMARY KEY,
    nom_suc TEXT NOT NULL,
    tip_punto TEXT,
    ciudad TEXT,
    depto TEXT,
    latitud REAL,
    longitud REAL,
    activo INTEGER
);

CREATE TABLE IF NOT EXISTS TB_OBLIGACIONES (
    id_oblig TEXT PRIMARY KEY,
    id_cli INTEGER,
    cod_prod TEXT,
    vr_aprobado REAL,
    vr_desembolsado REAL,
    sdo_capital REAL,
    vr_cuota REAL,
    fec_desembolso TEXT,
    fec_venc TEXT,
    dias_mora_act INTEGER,
    num_cuotas_pend INTEGER,
    calif_riesgo TEXT,
    FOREIGN KEY (id_cli) REFERENCES TB_CLIENTES_CORE(id_cli),
    FOREIGN KEY (cod_prod) REFERENCES TB_PRODUCTOS_CAT(cod_prod)
);

CREATE TABLE IF NOT EXISTS TB_MOV_FINANCIEROS (
    id_mov INTEGER PRIMARY KEY,
    id_cli INTEGER,
    cod_prod TEXT,
    num_cuenta TEXT,
    fec_mov TEXT,
    hra_mov TEXT,
    vr_mov REAL,
    tip_mov TEXT,
    cod_canal TEXT,
    cod_ciudad TEXT,
    cod_estado_mov TEXT,
    id_dispositivo TEXT,
    FOREIGN KEY (id_cli) REFERENCES TB_CLIENTES_CORE(id_cli),
    FOREIGN KEY (cod_prod) REFERENCES TB_PRODUCTOS_CAT(cod_prod)
);

CREATE TABLE IF NOT EXISTS TB_COMISIONES_LOG (
    id_comision INTEGER PRIMARY KEY,
    id_cli INTEGER,
    cod_prod TEXT,
    fec_cobro TEXT,
    vr_comision REAL,
    tip_comision TEXT,
    estado_cobro TEXT,
    FOREIGN KEY (id_cli) REFERENCES TB_CLIENTES_CORE(id_cli),
    FOREIGN KEY (cod_prod) REFERENCES TB_PRODUCTOS_CAT(cod_prod)
);