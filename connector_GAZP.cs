function Initialize() {
    StrategyName = "MyMaGAZP";
    AddParameter("P1", 0, "", 1);
    AddInput("Input1", Inputs.Candle, 1, true, "GAZP=МБ ЦК");
    LongLimit = 50;
    ShortLimit = -50;
}

function OnUpdate() {
    var Flag = "NULL";

    // Пока флаг равен "NULL", будем ждать обновления флага
    while (Flag == "NULL") {
        var webRequest = System.Net.WebRequest.Create("http://localhost:5000/getsignal/GAZP") as System.Net.HttpWebRequest;
        var response = webRequest.GetResponse();
        using (System.IO.StreamReader stream = new System.IO.StreamReader(response.GetResponseStream(), System.Text.Encoding.UTF8)) {
            Flag = stream.ReadToEnd();
        }

        // Устанавливаем задержку в 1 секунду
        System.Threading.Thread.Sleep(1000);
    }
    ShowMessage(Flag);
    if (Flag == "1") {
        EnterLong();
    }
    if (Flag == "-1") {
        EnterShort();
    }

    // Сбрасываем флаг на сервере, чтобы избежать задержки в следующий раз
    var resetRequest = System.Net.WebRequest.Create("http://localhost:5000/resetsignal/GAZP") as System.Net.HttpWebRequest;
    resetRequest.Method = "POST";
    var resetResponse = resetRequest.GetResponse();
}
