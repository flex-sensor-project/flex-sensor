using UnityEngine;
using System;
using System.Text;
using System.Net;
using System.Net.Sockets;
using System.Threading;

public class GloveReceiver : MonoBehaviour
{
    Thread receiveThread;
    UdpClient client;
    public int port = 5006;

    public float[] fingerData = new float[5];

    private bool isRunning = true;

    void Start()
    {
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true;
        receiveThread.Start();
        Debug.Log("UDP Receiver uruchomiony na porcie " + port);
    }

    private void ReceiveData()
    {
        client = new UdpClient(port);
        IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, 0);

        while (isRunning)
        {
            try
            {
                byte[] data = client.Receive(ref anyIP);
                
                string text = Encoding.UTF8.GetString(data);
                string[] splitData = text.Split(',');
                if (splitData.Length == 5)
                {
                    for (int i = 0; i < 5; i++)
                    {
                        fingerData[i] = System.Convert.ToSingle(splitData[i], System.Globalization.CultureInfo.InvariantCulture);
                    }
                }
            }
            catch (Exception err)
            {
                Debug.LogWarning("Błąd UDP: " + err.ToString());
            }
        }
    }

    void OnApplicationQuit()
    {
        isRunning = false;
		if(client != null){
			client.Close();
			client = null;
			
		}
        if (receiveThread != null) receiveThread.Abort();
        if (client != null) client.Close();
    }
	
	void onDestroy(){
        isRunning = false;
		if(client != null){
			client.Close();
			client = null;
			
		}
        if (receiveThread != null) receiveThread.Abort();
        if (client != null) client.Close();
    }
}