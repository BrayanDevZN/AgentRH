"""importa a função cria as tabelas e junta com a engine"""


if __name__ == "__main__":

    import sys
    if sys.argv[1] == "make_migration_tables":

        from src.database.migration.tables import migration_db
        from src.service.db.connetion import engine


        migration_db(engine=engine)

    else:

        raise ValueError(f"Not exepted arg {sys.argv[1]}")