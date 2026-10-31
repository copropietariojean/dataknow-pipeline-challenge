# Diagrama Entidad-Relación (Modelo Relacional Fuente) - FinBank

Este modelo representa la estructura del sistema transaccional origen para el escenario de Banca y Servicios Financieros.

```mermaid
erDiagram
    TB_CLIENTES_CORE ||--o{ TB_MOV_FINANCIEROS : "1 a N (id_cli)"
    TB_CLIENTES_CORE ||--o{ TB_OBLIGACIONES : "1 a N (id_cli)"
    TB_CLIENTES_CORE ||--o{ TB_COMISIONES_LOG : "1 a N (id_cli)"
    
    TB_PRODUCTOS_CAT ||--o{ TB_MOV_FINANCIEROS : "1 a N (cod_prod)"
    TB_PRODUCTOS_CAT ||--o{ TB_OBLIGACIONES : "1 a N (cod_prod)"
    TB_PRODUCTOS_CAT ||--o{ TB_COMISIONES_LOG : "1 a N (cod_prod)"

    TB_CLIENTES_CORE {
        int id_cli PK
        string nomb_cli
        string apell_cli
        string tip_doc
        string num_doc
        date fec_nac
        date fec_alta
        string cod_segmento
        int score_buro
        string ciudad_res
        string depto_res
        string estado_cli
        string canal_adquis
    }

    TB_PRODUCTOS_CAT {
        string cod_prod PK
        string desc_prod
        string tip_prod
        decimal tasa_ea
        int plazo_max_meses
        decimal cuota_min
        decimal comision_admin
        string estado_prod
    }

    TB_SUCURSALES_RED {
        string cod_suc PK
        string nom_suc
        string tip_punto
        string ciudad
        string depto
        decimal latitud
        decimal longitud
        int activo
    }

    TB_OBLIGACIONES {
        string id_oblig PK
        int id_cli FK
        string cod_prod FK
        decimal vr_aprobado
        decimal vr_desembolsado
        decimal sdo_capital
        decimal vr_cuota
        date fec_desembolso
        date fec_venc
        int dias_mora_act
        int num_cuotas_pend
        string calif_riesgo
    }

    TB_MOV_FINANCIEROS {
        int id_mov PK
        int id_cli FK
        string cod_prod FK
        string num_cuenta
        date fec_mov
        time hra_mov
        decimal vr_mov
        string tip_mov
        string cod_canal
        string cod_ciudad
        string cod_estado_mov
        string id_dispositivo
    }

    TB_COMISIONES_LOG {
        int id_comision PK
        int id_cli FK
        string cod_prod FK
        date fec_cobro
        decimal vr_comision
        string tip_comision
        string estado_cobro
    }