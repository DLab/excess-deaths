var mysql = require("mysql");
const R = require("rambda");
const neatCsv = require("neat-csv");
const fs = require("fs");
const exec = require("child_process").exec;
const credentials = require("./credentials.json");

const filesDaily = ["Excces_dead_nac_daily.csv", "Excces_dead_reg_daily.csv"];
const filesWeekly = [
  "Excces_dead_nac_weekly.csv",
  "Excces_dead_reg_weekly.csv",
];

var connection = mysql.createConnection(credentials);

connection.connect();

let count = 0;

exec("sh csv.sh", (error, stdout, stderr) => {
  if (error) {
    console.error(`exec error: ${error}`);
    return;
  }
  filesDaily.forEach((file) => {
    const csv = fs.readFileSync(`./${file}`);
    let datosDiarios = {
      fecha: [],
      dia: [],
      defunciones_totales: [],
      defunciones_covid: [],
      media: [],
      defunciones_no_covid: [],
      exceso_media: [],
      exceso_2S: [],
      exceso_1S: [],
      exceso_minus1S: [],
      exceso_minus2S: [],
      region: [],
    };
    neatCsv(csv).then((raw) => {
      raw.forEach((data) => {
        datosDiarios.fecha.push(data.Fecha);
        datosDiarios.dia.push(data.dia);
        datosDiarios.defunciones_totales.push(data["Defunciones 2020"]);
        datosDiarios.defunciones_covid.push(data["Defunciones Covid"]);
        datosDiarios.media.push(
          data["Media poderanda de defunciones proyectada 2020"]
        );
        datosDiarios.defunciones_no_covid.push(
          data["Defunciones sin causal Covid"]
        );
        datosDiarios.exceso_media.push(
          data["Exceso de muertes media poderada"]
        );
        datosDiarios.exceso_2S.push(data["Exceso de muertes 2S"]);
        datosDiarios.exceso_1S.push(data["Exceso de muertes 1S"]);
        datosDiarios.exceso_minus1S.push(data["Exceso de muertes -1S"]);
        datosDiarios.exceso_minus2S.push(data["Exceso de muertes -2S"]);
        datosDiarios.region.push(data["Codigo region"]);
      });

      let transpose = R.transpose([
        datosDiarios.fecha,
        datosDiarios.dia,
        datosDiarios.defunciones_totales,
        datosDiarios.defunciones_covid,
        datosDiarios.media,
        datosDiarios.defunciones_no_covid,
        datosDiarios.exceso_media,
        datosDiarios.exceso_2S,
        datosDiarios.exceso_1S,
        datosDiarios.exceso_minus1S,
        datosDiarios.exceso_minus2S,
        datosDiarios.region,
      ]);

      var sql = `insert
	    into
	    exceso_de_muertes_diario values ?`;
      try {
        connection.query("delete from exceso_de_muertes_diario", function () {
          connection.query(sql, [transpose], function (err, rows) {
            console.log(err);
            console.log(rows);
            count++;
            if (count === 4) return process.exit(22);
          });
        });
      } catch (e) {
        console.error(e);
      }
    });
  });

  filesWeekly.forEach((file) => {
    const csv = fs.readFileSync(`./${file}`);
    let datosDiarios = {
      semana: [],
      defunciones_totales: [],
      defunciones_covid: [],
      media: [],
      defunciones_no_covid: [],
      exceso_media: [],
      exceso_2S: [],
      exceso_1S: [],
      exceso_minus1S: [],
      exceso_minus2S: [],
      region: [],
    };
    neatCsv(csv).then((raw) => {
      raw.forEach((data) => {
        datosDiarios.semana.push(data.Semana);
        datosDiarios.defunciones_totales.push(data["Defunciones_2020"]);
        datosDiarios.defunciones_covid.push(data["Defunciones_Covid"]);
        datosDiarios.media.push(data["Media_2020"]);
        datosDiarios.defunciones_no_covid.push(data["Defunciones_no_Covid"]);
        datosDiarios.exceso_media.push(data["Defunsiones_media"]);
        datosDiarios.exceso_2S.push(data["2S"]);
        datosDiarios.exceso_1S.push(data["1S"]);
        datosDiarios.exceso_minus1S.push(data["-1S"]);
        datosDiarios.exceso_minus2S.push(data["-2S"]);
        datosDiarios.region.push(data["Codigo region"]);
      });

      let transpose = R.transpose([
        datosDiarios.semana,
        datosDiarios.defunciones_totales,
        datosDiarios.defunciones_covid,
        datosDiarios.media,
        datosDiarios.defunciones_no_covid,
        datosDiarios.exceso_media,
        datosDiarios.exceso_2S,
        datosDiarios.exceso_1S,
        datosDiarios.exceso_minus1S,
        datosDiarios.exceso_minus2S,
        datosDiarios.region,
      ]);

      var sql = `insert
	    into
	    exceso_de_muertes_semanal values ?`;
      try {
        connection.query("delete from exceso_de_muertes_semanal", function () {
          connection.query(sql, [transpose], function (err, rows) {
            console.log(err);
            console.log(rows);
            count++;
            if (count === 4) return process.exit(22);
          });
        });
      } catch (e) {
        console.error(e);
      }
    });
    console.log("END?");
  });

  console.log(`stdout: ${stdout}`);
  console.error(`stderr: ${stderr}`);
});

process.on("exit", function (code) {
  return console.log(`About to exit with code ${code}`);
});
