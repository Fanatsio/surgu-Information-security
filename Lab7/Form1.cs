using System.Text;
using System.Net;
using System.Net.Sockets;
using System.Security.Cryptography;

namespace def7
{
    public partial class Form1 : Form
    {
        private TextBox txtIP;
        private TextBox txtPort;
        private Button btnStart;
        private TextBox txtChat;
        private TextBox txtMessage;
        private Button btnSend;

        private TcpListener listener;
        private TcpClient client;
        private NetworkStream netStream;
        private Thread listenThread;
        private Thread receiveThread;

        private readonly RSA ourRSA;
        private RSA otherSideRSA;

        private bool stopThreads = false;

        private byte[] aesKey;
        private byte[] aesIV;
        private bool aesReady = false;

        public Form1()
        {
            InitializeComponent();
            SetupUI();
            ourRSA = RSA.Create();
        }

        private void SetupUI()
        {
            this.Text = "7 лабораторная работа по дисциплине \"Защита информации\"";
            this.Width = 800;
            this.Height = 600;
            this.BackColor = Color.FromArgb(30, 30, 30);
            this.ForeColor = Color.White;

            rbServer = new RadioButton
            {
                Text = "Сервер",
                ForeColor = Color.White,
                Location = new Point(20, 20),
                AutoSize = true
            };

            rbClient = new RadioButton
            {
                Text = "Клиент",
                ForeColor = Color.White,
                Location = new Point(20, 40),
                AutoSize = true
            };
            rbServer.Checked = true;

            Label lblIP = new()
            {
                Text = "IP:",
                ForeColor = Color.White,
                Location = new Point(15, 70),
                AutoSize = true
            };

            txtIP = new TextBox
            {
                Location = new Point(40, 67),
                Width = 120,
                BackColor = Color.FromArgb(60, 60, 60),
                ForeColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle,
                Text = "192.168.210.96"
            };

            Label lblPort = new()
            {
                Text = "Порт:",
                ForeColor = Color.White,
                Location = new Point(15, 100),
                AutoSize = true
            };

            txtPort = new TextBox
            {
                Location = new Point(60, 98),
                Width = 100,
                BackColor = Color.FromArgb(60, 60, 60),
                ForeColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle,
                Text = "5000"
            };

            btnStart = new Button
            {
                Text = "Запуск / Подключение",
                Location = new Point(15, 130),
                Width = 180,
                Height = 30,
                BackColor = Color.FromArgb(0, 120, 215),
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat,
                Font = new Font("Segoe UI", 9, FontStyle.Bold)
            };
            btnStart.FlatAppearance.BorderSize = 0;
            btnStart.Click += BtnStart_Click;

            txtChat = new TextBox()
            {
                Left = 210,
                Top = 10,
                Width = 560,
                Height = 450,
                Multiline = true,
                ScrollBars = ScrollBars.Vertical,
                ReadOnly = true
            };

            txtMessage = new TextBox() 
            { 
                Left = 210, 
                Top = 470,
                Width = 420, 
                Height = 60, 
                Multiline = true, 
                ScrollBars = ScrollBars.Vertical 
            };
            
            btnSend = new Button() 
            { 
                Text = "Отправить сообщение", 
                Left = 660, 
                Top = 470, 
                Width = 100, 
                Height = 60,
                BackColor = Color.Green,
                ForeColor = Color.White,
            };
            btnSend.Click += BtnSend_Click;

            this.Controls.Add(rbServer);
            this.Controls.Add(rbClient);
            this.Controls.Add(lblIP);
            this.Controls.Add(txtIP);
            this.Controls.Add(lblPort);
            this.Controls.Add(txtPort);
            this.Controls.Add(btnStart);
            this.Controls.Add(txtChat);
            this.Controls.Add(txtMessage);
            this.Controls.Add(btnSend);


        }

        private void BtnStart_Click(object sender, EventArgs e)
        {
            if (rbServer.Checked) StartServer();
            else StartClient();
        }

        private void BtnSend_Click(object sender, EventArgs e)
        {
            if (netStream == null) return;
            if (!netStream.CanWrite) return;
            if (string.IsNullOrWhiteSpace(txtMessage.Text)) return;
            if (!aesReady)
            {
                AppendChat("AES-ключ не готов. Сообщение не будет отправлено.");
                return;
            }
            if (otherSideRSA == null)
            {
                AppendChat("Нет публичного RSA-ключа собеседника.");
                return;
            }

            string message = txtMessage.Text.Trim();
            byte[] messageBytes = Encoding.UTF8.GetBytes(message);

            byte[] signature = ourRSA.SignData(messageBytes, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
            byte[] sigLenBytes = BitConverter.GetBytes(signature.Length);

            using (MemoryStream ms = new())
            {
                ms.Write(sigLenBytes, 0, sigLenBytes.Length);
                ms.Write(signature, 0, signature.Length);
                ms.Write(messageBytes, 0, messageBytes.Length);

                byte[] combined = ms.ToArray();
                byte[] encrypted = AesEncrypt(combined, aesKey, aesIV);

                byte[] lengthBytes = BitConverter.GetBytes(encrypted.Length);
                netStream.Write(lengthBytes, 0, lengthBytes.Length);
                netStream.Write(encrypted, 0, encrypted.Length);
            }

            AppendChat("Вы: " + message);
            txtMessage.Clear();
        }

        private void StartServer()
        {
            stopThreads = false;
            int port = int.Parse(txtPort.Text);
            listener = new TcpListener(IPAddress.Any, port);
            listener.Start();
            AppendChat("Сервер запущен. Ожидаем подключения...");

            listenThread = new Thread(() =>
            {
                try
                {
                    client = listener.AcceptTcpClient();
                    netStream = client.GetStream();
                    AppendChatThreadSafe("Клиент подключился");

                    ReceiveOtherSidePublicKey();
                    SendOurPublicKey();

                    GenerateAES();
                    SendAESKeyToClient();

                    aesReady = true;

                    receiveThread = new Thread(ReceiveLoop);
                    receiveThread.Start();
                }
                catch (Exception ex)
                {
                    AppendChatThreadSafe("Ошибка на сервере: " + ex.Message);
                }
            })
            {
                IsBackground = true
            };
            listenThread.Start();
        }

        private void StartClient()
        {
            stopThreads = false;
            string ip = txtIP.Text.Trim();
            int port = int.Parse(txtPort.Text);

            try
            {
                client = new TcpClient();
                client.Connect(IPAddress.Parse(ip), port);
                netStream = client.GetStream();
                AppendChat("Клиент подлючился к серверу.");

                SendOurPublicKey();
                ReceiveOtherSidePublicKey();

                ReceiveAESKeyFromServer();

                aesReady = true;

                receiveThread = new Thread(ReceiveLoop);
                receiveThread.Start();
            }
            catch (Exception ex)
            {
                AppendChat("Ошибка при подключении клиента: " + ex.Message);
            }
        }

        private void ReceiveOtherSidePublicKey()
        {
            try
            {
                byte[] lengthBytes = new byte[4];
                ReadExact(lengthBytes, 4);
                int keyLength = BitConverter.ToInt32(lengthBytes, 0);

                byte[] keyBytes = new byte[keyLength];
                ReadExact(keyBytes, keyLength);

                string publicKeyXml = Encoding.UTF8.GetString(keyBytes);
                RSA rsa = RSA.Create();
                rsa.FromXmlString(publicKeyXml);
                otherSideRSA = rsa;

                AppendChatThreadSafe("Получен публичный ключ собеседника.");
            }
            catch (Exception ex)
            {
                AppendChatThreadSafe("Ошибка получения публичного ключа: " + ex.Message);
            }
        }

        private void SendOurPublicKey()
        {
            try
            {
                string xmlPublicKey = ourRSA.ToXmlString(false);
                byte[] keyBytes = Encoding.UTF8.GetBytes(xmlPublicKey);
                byte[] lengthBytes = BitConverter.GetBytes(keyBytes.Length);
                netStream.Write(lengthBytes, 0, lengthBytes.Length);
                netStream.Write(keyBytes, 0, keyBytes.Length);
                AppendChatThreadSafe("Наш публичный ключ отправлен.");
            }
            catch (Exception ex)
            {
                AppendChatThreadSafe("Ошибка отправки публичного ключа: " + ex.Message);
            }
        }

        private void GenerateAES()
        {
            using Aes aes = Aes.Create();
            aes.KeySize = 256;
            aes.GenerateKey();
            aes.GenerateIV();
            aesKey = aes.Key;
            aesIV = aes.IV;
        }

        private void SendAESKeyToClient()
        {
            if (otherSideRSA == null) return;

            using (MemoryStream ms = new())
            {
                ms.Write(BitConverter.GetBytes(aesKey.Length), 0, 4);
                ms.Write(aesKey, 0, aesKey.Length);
                ms.Write(BitConverter.GetBytes(aesIV.Length), 0, 4);
                ms.Write(aesIV, 0, aesIV.Length);

                byte[] rawData = ms.ToArray();
                byte[] encrypted = otherSideRSA.Encrypt(rawData, RSAEncryptionPadding.Pkcs1);

                byte[] lengthBytes = BitConverter.GetBytes(encrypted.Length);
                netStream.Write(lengthBytes, 0, lengthBytes.Length);
                netStream.Write(encrypted, 0, encrypted.Length);
            }

            AppendChatThreadSafe("AES-ключ отправлен клиенту.");
        }

        private void ReceiveAESKeyFromServer()
        {
            if (otherSideRSA == null) return;

            try
            {
                byte[] lenBytes = new byte[4];
                ReadExact(lenBytes, 4);
                int encLen = BitConverter.ToInt32(lenBytes, 0);

                byte[] encBlock = new byte[encLen];
                ReadExact(encBlock, encLen);

                byte[] rawData = ourRSA.Decrypt(encBlock, RSAEncryptionPadding.Pkcs1);

                int offset = 0;
                int keyLen = BitConverter.ToInt32(rawData, offset);
                offset += 4;

                aesKey = new byte[keyLen];
                Buffer.BlockCopy(rawData, offset, aesKey, 0, keyLen);
                offset += keyLen;

                int ivLen = BitConverter.ToInt32(rawData, offset);
                offset += 4;

                aesIV = new byte[ivLen];
                Buffer.BlockCopy(rawData, offset, aesIV, 0, ivLen);

                AppendChatThreadSafe("Получен AES-ключ от сервера.");
            }
            catch (Exception ex)
            {
                AppendChatThreadSafe("Ошибка получения AES-ключа: " + ex.Message);
            }
        }

        private void ReceiveLoop()
        {
            while (!stopThreads)
            {
                try
                {
                    byte[] lengthBytes = new byte[4];
                    int readCount = netStream.Read(lengthBytes, 0, 4);
                    if (readCount == 0) break;
                    int dataLength = BitConverter.ToInt32(lengthBytes, 0);

                    byte[] encryptedData = new byte[dataLength];
                    int offset = 0;
                    while (offset < dataLength)
                    {
                        int r = netStream.Read(encryptedData, offset, dataLength - offset);
                        if (r == 0) break;
                        offset += r;
                    }

                    if (!aesReady) continue;

                    byte[] decrypted = AesDecrypt(encryptedData, aesKey, aesIV);

                    int sigLen = BitConverter.ToInt32(decrypted, 0);
                    byte[] signBytes = new byte[sigLen];
                    Buffer.BlockCopy(decrypted, 4, signBytes, 0, sigLen);

                    int msgOffset = 4 + sigLen;
                    int msgLen = decrypted.Length - msgOffset;
                    byte[] messageBytes = new byte[msgLen];
                    Buffer.BlockCopy(decrypted, msgOffset, messageBytes, 0, msgLen);

                    bool valid = false;
                    if (otherSideRSA != null)
                    {
                        valid = otherSideRSA.VerifyData(
                            messageBytes,
                            signBytes,
                            HashAlgorithmName.SHA256,
                            RSASignaturePadding.Pkcs1
                        );
                    }

                    string message = Encoding.UTF8.GetString(messageBytes);

                    if (valid) AppendChatThreadSafe("Собеседник: " + message);
                    else AppendChatThreadSafe("Сообщение с НЕВЕРНОЙ подписью!");
                }
                catch (Exception ex)
                {
                    if (!stopThreads) AppendChatThreadSafe("Ошибка приёма: " + ex.Message);
                    break;
                }
            }
        }

        private static byte[] AesEncrypt(byte[] data, byte[] key, byte[] iv)
        {
            using Aes aes = Aes.Create();
            aes.Key = key;
            aes.IV = iv;
            aes.Mode = CipherMode.CBC;
            aes.Padding = PaddingMode.PKCS7;
            using MemoryStream ms = new();
            using (ICryptoTransform encryptor = aes.CreateEncryptor())
            using (CryptoStream cs = new(ms, encryptor, CryptoStreamMode.Write))
            {
                cs.Write(data, 0, data.Length);
            }
            return ms.ToArray();
        }

        private static byte[] AesDecrypt(byte[] data, byte[] key, byte[] iv)
        {
            using Aes aes = Aes.Create();
            aes.Key = key;
            aes.IV = iv;
            aes.Mode = CipherMode.CBC;
            aes.Padding = PaddingMode.PKCS7;
            using MemoryStream ms = new();
            using (ICryptoTransform decryptor = aes.CreateDecryptor())
            using (CryptoStream cs = new(ms, decryptor, CryptoStreamMode.Write))
            {
                cs.Write(data, 0, data.Length);
            }
            return ms.ToArray();
        }

        private void ReadExact(byte[] buffer, int size)
        {
            int offset = 0;
            while (offset < size)
            {
                int r = netStream.Read(buffer, offset, size - offset);
                if (r == 0) throw new Exception("ОШИБКА.");
                offset += r;
            }
        }

        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            stopThreads = true;
            try
            {
                listener?.Stop();
                client?.Close();
            }
            catch { }
            base.OnFormClosing(e);
        }

        private void AppendChat(string text)
        {
            txtChat.AppendText(text + Environment.NewLine);
        }

        private void AppendChatThreadSafe(string text)
        {
            if (txtChat.InvokeRequired) txtChat.Invoke(new Action<string>(AppendChat), text);
            else AppendChat(text);
        }

        private void Form1_Load(object sender, EventArgs e) { }
    }
}
