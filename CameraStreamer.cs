using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;
using UnityEngine.UI;

public class CameraStreamer : MonoBehaviour
{
    [Header("摄像头设置")]
    public Camera targetCamera;  // 拖入场景中的摄像头
    public RawImage previewImage; // UI上的RawImage（可选预览）
    public int streamWidth = 640;
    public int streamHeight = 480;
    [SerializeField]
    private int _targetFPS = 30;

    public int targetFPS
    {
        get => _targetFPS;
        set => _targetFPS = Mathf.Max(1, value); // 强制最小为1
    }
    private float nextFrameTime;

    [Header("网络设置")]
    public int vsCodePort = 8080; // VS Code调试端口
    public int dataStreamPort = 32000; // 数据传输端口
    public Texture2D cameraTexture;
    private RenderTexture renderTexture;
    private TcpListener dataListener;
    private bool isStreaming = true;
    

    void Start()
    {
        InitializeCamera();
        InitializeNetwork();
        Debug.Log("<color=green>系统初始化完成</color>");
        targetFPS = Mathf.Max(1, targetFPS); 
    }

    void InitializeCamera()
    {
        // 确保摄像头不为空
        if (targetCamera == null) 
        {
            targetCamera = Camera.main;
            if (targetCamera == null)
            {
                Debug.LogError("未找到主摄像头！");
                return;
            }
        }
        // 创建渲染纹理和摄像头纹理
        renderTexture = new RenderTexture(streamWidth, streamHeight, 24);
        cameraTexture = new Texture2D(streamWidth, streamHeight, TextureFormat.RGB24, false);
        targetCamera.enabled = true; // 确保摄像头启用
        // 配置摄像头
        // 初始化 Texture2D
        cameraTexture = new Texture2D(streamWidth, streamHeight, TextureFormat.RGB24, false);

        // 可选：在UI上显示预览
        if (previewImage != null)
        {
            previewImage.texture = cameraTexture;
            Debug.Log("摄像头预览已启用");
        }
    }

    void InitializeNetwork()
    {
        // 启动TCP服务器（用于发送画面数据）
        dataListener = new TcpListener(IPAddress.Any, dataStreamPort);
        dataListener.Start();
        _ = StartDataStreamAsync(); // 异步启动数据流

        // 尝试连接VS Code
        _ = ConnectToVSCodeAsync();
    }

    async Task ConnectToVSCodeAsync()
    {
        Debug.Log($"<color=cyan>尝试连接VS Code (127.0.0.1:{vsCodePort})...</color>");
        
        try
        {
            using (TcpClient vsCodeClient = new TcpClient())
            {
                await vsCodeClient.ConnectAsync("127.0.0.1", vsCodePort);
                
                if (vsCodeClient.Connected)
                {
                    // 发送握手信号
                    byte[] signal = Encoding.ASCII.GetBytes("UNITY_CAMERA_READY");
                    await vsCodeClient.GetStream().WriteAsync(signal, 0, signal.Length);
                    Debug.Log("<color=green>✓ VS Code连接成功，信号已发送</color>");
                }
            }
        }
        catch (System.Exception e)
        {
            Debug.LogWarning($"<color=orange>VS Code连接失败: {e.Message}</color>");
        }
    }

    async Task StartDataStreamAsync()
    {
        Debug.Log($"<color=cyan>数据流服务器已启动 (0.0.0.0:{dataStreamPort})</color>");
        
        while (isStreaming)
        {
            using (TcpClient client = await dataListener.AcceptTcpClientAsync())
            {
                Debug.Log($"<color=blue>客户端连接: {client.Client.RemoteEndPoint}</color>");
                await SendCameraFrameAsync(client);
            }
        }
    }

    async Task SendCameraFrameAsync(TcpClient client)
    {
        try
        {
            // 捕获当前帧到Texture2D
            RenderTexture.active = renderTexture;
            cameraTexture.ReadPixels(new Rect(0, 0, streamWidth, streamHeight), 0, 0);
            cameraTexture.Apply();
            RenderTexture.active = null;

            // 编码为JPG并发送
            byte[] frameData = cameraTexture.EncodeToJPG();
            NetworkStream stream = client.GetStream();
            await stream.WriteAsync(frameData, 0, frameData.Length);
            
            Debug.Log($"<color=green>已发送帧数据 ({frameData.Length} 字节)</color>");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"<color=red>发送失败: {e.Message}</color>");
        }
    }

    void Update()
    {
        if (Time.time >= nextFrameTime)
        {
            nextFrameTime = Time.time + (1f / targetFPS); // 计算下一帧时间
            // 执行逻辑...
        }
    }

    void OnDestroy()
    {
        isStreaming = false;
        dataListener?.Stop();
        Debug.Log("<color=red>系统已关闭</color>");
    }
}