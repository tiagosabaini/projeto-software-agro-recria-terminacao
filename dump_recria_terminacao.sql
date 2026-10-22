BEGIN TRANSACTION;
CREATE TABLE consumo_sal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lote_id INTEGER,
                    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    qtd_sacos REAL,
                    peso_saco_kg REAL,
                    dias INTEGER,
                    qtd_bois INTEGER,
                    gramas_cab_dia REAL,
                    FOREIGN KEY(lote_id) REFERENCES lotes(id) ON DELETE CASCADE
                );
CREATE TABLE cotacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            frigorifico TEXT UNIQUE,
            preco REAL
        );
INSERT INTO "cotacoes" VALUES(1,'JBS',300.0);
INSERT INTO "cotacoes" VALUES(2,'Frigon',310.0);
INSERT INTO "cotacoes" VALUES(3,'Minerva',320.0);
CREATE TABLE despesas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lote_id INTEGER,
                    categoria TEXT,
                    valor REAL,
                    observacao TEXT,
                    FOREIGN KEY(lote_id) REFERENCES lotes(id) ON DELETE CASCADE
                );
CREATE TABLE lotes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    identificacao TEXT NOT NULL,
                    fase_atual TEXT NOT NULL,
                    categoria_animal TEXT,
                    data_inicio TEXT,
                    qtd_cabecas INTEGER,
                    custo_bezerro_unitario REAL,
                    custo_total_compra REAL,
                    valor_venda_total REAL,
                    total_arrobas_vendidas REAL,
                    status TEXT DEFAULT 'Em Andamento'
                , frigorifico_comprador TEXT);
INSERT INTO "lotes" VALUES(1,'gf','Recria','Bezerro',NULL,5,3.0,15.0,NULL,NULL,'Em Andamento',NULL);
CREATE TABLE pesagens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lote_id INTEGER,
                    peso REAL,
                    data TEXT,
                    FOREIGN KEY(lote_id) REFERENCES lotes(id) ON DELETE CASCADE
                );
CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            usuario TEXT UNIQUE,
            senha TEXT,
            nivel_acesso TEXT
        );
INSERT INTO "usuarios" VALUES(1,'Produtor Rural','admin','scrypt:32768:8:1$8iHG9EoUrbaoRFNI$e2f852ef15d02fe1e64d339ca31d744db65289441f07210067062d3c2569b34b4dd4aeae918071e155375e2c7cdc94986184722ff57fa55a99fe6f932bbf9755','comum');
INSERT INTO "usuarios" VALUES(2,'Tiago Sabaini (SysAdmin)','tiago','scrypt:32768:8:1$0CsaJsBGQ5IsG4LE$9f4d2d4b7f54f4111cd8718bdf8ee26cefb74db3e5f2a54eda69218f4239efdf096752518cdfc0f5a10c92decf9235c164814f698c55b7eedda7febbad9c225a','sysadmin');
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('usuarios',2);
INSERT INTO "sqlite_sequence" VALUES('cotacoes',3);
INSERT INTO "sqlite_sequence" VALUES('lotes',1);
COMMIT;
