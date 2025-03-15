import subprocess
import json
import time
 
def get_gpu_status(host):
   # SSH命令获取GPU状态，这里假设服务器上已经安装了nvidia-smi工具
   command = f"ssh {host} nvidia-smi --query-gpu=index,name,utilization.gpu,utilization.memory,memory.total,temperature.gpu --format=csv,noheader,nounits" if host != 'l2' else "nvidia-smi --query-gpu=index,name,utilization.gpu,utilization.memory,memory.total,temperature.gpu --format=csv,noheader,nounits"
   try:
       result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
       output = result.stdout.decode('utf-8')
       return output
   except subprocess.CalledProcessError as e:
       print(f"Error executing SSH command: {e.stderr.decode('utf-8')}")
       return None
 
def parse_gpu_output(output):
   # 解析nvidia-smi的输出
   lines = output.strip().split('\n')
   gpu_data = []
   for line in lines:
       try:
        # gpu_utilization, memory_used, memory_total = map(int, info.split(', '))
        parts = line.split(', ')
        tmppp = int(parts[0])
       except:
        return output
       gpu_info = {
           'index': int(parts[0]),
           'name': parts[1],
           'gpu_utilization': int(parts[2]),
           'memory_utilization': int(parts[3]),
           'memory_total': int(parts[4]),
           'temperature': int(parts[5])
       }
       gpu_data.append(gpu_info)
   message = '\n'.join([f"GPU{gpu_data[i]['index']} {gpu_data[i]['name']}  utilization {gpu_data[i]['gpu_utilization']}%    mem {round(gpu_data[i]['memory_utilization']/1024)}GB/{round(gpu_data[i]['memory_total']/1024)}GB    temp {gpu_data[i]['temperature']}°" for i in range(len(gpu_data))])
   return message
 
def save_to_json(data, filename):
   # 将数据保存到JSON文件
   with open(filename, 'w') as f:
       json.dump(data, f, indent=4)
 
def main():
   hosts = ['l1', 'l2', 'l3']
   interval = 60  # 每隔60秒获取一次GPU状态
   json_filename = 'gpu_status.json'
   
   while True:
       outputs = []
       for host in hosts:
           output = get_gpu_status(host)
           if output:
             gpu_data = parse_gpu_output(output)
             outputs.append({host: f"Machine {host}:\n" + gpu_data})
       save_to_json(outputs, json_filename)
       time.sleep(interval)
 
if __name__ == "__main__":
   main()
