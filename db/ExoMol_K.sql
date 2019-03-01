BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "energylevel" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"isotopologue"	INTEGER,
	"exomol_ID"	INTEGER,
	"energy"	INTEGER,
	"J"	INTEGER,
	"Tparity"	TEXT,
	"Rparity"	TEXT,
	"state"	TEXT,
	"v"	INTEGER,
	"Lambda"	INTEGER,
	"Sigma"	INTEGER,
	"Omega"	INTEGER,
	FOREIGN KEY("isotopologue") REFERENCES "Isotopologue"("id")
);
CREATE TABLE IF NOT EXISTS "transition" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"isotopologue"	INTEGER,
	"exomol_ID"	TEXT,
	"upper"	INTEGER,
	"lower"	INTEGER,
	"einstien_A"	REAL,
	"intensity"	REAL,
	"wavenumber"	REAL,
	FOREIGN KEY("isotopologue") REFERENCES "Isotopologue"("id"),
	FOREIGN KEY("upper") REFERENCES "energylevel"("id"),
	FOREIGN KEY("lower") REFERENCES "energylevel"("id")
);
CREATE TABLE IF NOT EXISTS "isotopologue" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"name"	INTEGER NOT NULL,
	"temperature"	INTEGER NOT NULL,
	"g_ns"	INTEGER NOT NULL,
	"Q_T"	REAL
);
COMMIT;
