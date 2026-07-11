import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
  CartesianGrid,
} from 'recharts';

const COLORS = ['#00f2fe', '#4facfe', '#c084fc', '#10b981', '#f59e0b'];

export function Analytics({ data, loading }) {
  if (loading || !data) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-4">
        <div className="w-12 h-12 rounded-full border-4 border-t-blue-400 border-gray-800 animate-spin"></div>
        <p className="text-gray-400 text-sm">Đang tải biểu đồ xu hướng thị trường...</p>
      </div>
    );
  }

  // Format tech stack data
  const techData = Object.entries(data.tech_stacks || {})
    .map(([name, count]) => ({
      name: name === 'golang' ? 'Go' : name.charAt(0).toUpperCase() + name.slice(1),
      count,
    }))
    .sort((a, b) => b.count - a.count);

  // Format remote policies data
  const remoteData = Object.entries(data.remote_policies || {}).map(([name, value]) => ({
    name: name.toLowerCase() === 'unknown' ? 'Chưa có thông tin' : name,
    value,
  }));

  // Format locations data
  const locationData = Object.entries(data.locations || {}).map(([name, value]) => ({
    name: name.toLowerCase() === 'unknown' ? 'Chưa có thông tin' : name,
    value,
  }));

  // Format salary data (convert to Million VND)
  const salaryData = (data.salary_trends || []).map((item) => ({
    seniority: item.seniority.toLowerCase() === 'unknown' ? 'Chưa có thông tin' : item.seniority,
    Min: parseFloat((item.avg_min_vnd / 1000000).toFixed(1)),
    Max: parseFloat((item.avg_max_vnd / 1000000).toFixed(1)),
  }));

  const renderCustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-[#111625]/90 border border-gray-800 p-3 rounded-lg shadow-xl backdrop-blur-md">
          <p className="text-xs font-bold text-gray-300 mb-1">{label}</p>
          {payload.map((p, idx) => (
            <p key={idx} className="text-sm font-semibold" style={{ color: p.color }}>
              {p.name}: {p.value}M VND
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  const renderCountTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-[#111625]/90 border border-gray-800 p-3 rounded-lg shadow-xl backdrop-blur-md">
          <p className="text-xs font-bold text-gray-300 mb-1">{label}</p>
          <p className="text-sm font-semibold text-blue-400">
            Số lượng: {payload[0].value} bài tuyển dụng
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pb-12">
      {/* Salary Trends */}
      <div className="glass-panel p-5 rounded-xl">
        <h3 className="text-lg font-bold text-gray-200 mb-4">
          Mức lương trung bình theo Cấp bậc (Triệu VND)
        </h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={salaryData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
              <XAxis dataKey="seniority" stroke="#6b7280" fontSize={12} tickLine={false} />
              <YAxis stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} />
              <Tooltip content={renderCustomTooltip} />
              <Legend verticalAlign="top" height={36} iconType="circle" />
              <Bar dataKey="Min" name="Lương Min" fill="#00f2fe" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Max" name="Lương Max" fill="#4facfe" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Tech Stack Demand */}
      <div className="glass-panel p-5 rounded-xl">
        <h3 className="text-lg font-bold text-gray-200 mb-4">
          Nhu cầu Công nghệ (Số lượng bài đăng tuyển)
        </h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={techData.slice(0, 8)}
              layout="vertical"
              margin={{ top: 5, right: 10, left: 10, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" horizontal={false} />
              <XAxis
                type="number"
                stroke="#6b7280"
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                dataKey="name"
                type="category"
                stroke="#6b7280"
                fontSize={12}
                tickLine={false}
              />
              <Tooltip content={renderCountTooltip} />
              <Bar dataKey="count" fill="url(#techGrad)" radius={[0, 4, 4, 0]} barSize={16}>
                <defs>
                  <linearGradient id="techGrad" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="#4facfe" />
                    <stop offset="100%" stopColor="#00f2fe" />
                  </linearGradient>
                </defs>
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Location Distribution */}
      <div className="glass-panel p-5 rounded-xl">
        <h3 className="text-lg font-bold text-gray-200 mb-4">Phân bố Địa lý Tuyển dụng</h3>
        <div className="h-80 flex items-center justify-center">
          <div className="w-3/5 h-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={locationData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {locationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="w-2/5 flex flex-col gap-2 justify-center pl-4 border-l border-gray-800">
            {locationData.map((item, index) => (
              <div key={index} className="flex items-center gap-2 text-xs">
                <span
                  className="w-3 h-3 rounded-full shrink-0"
                  style={{ backgroundColor: COLORS[index % COLORS.length] }}
                ></span>
                <span className="text-gray-300 font-semibold truncate">{item.name}:</span>
                <span className="text-gray-400">{item.value} tin</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Remote Policy Distribution */}
      <div className="glass-panel p-5 rounded-xl">
        <h3 className="text-lg font-bold text-gray-200 mb-4">Phân phối Chính sách làm việc</h3>
        <div className="h-80 flex items-center justify-center">
          <div className="w-3/5 h-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={remoteData}
                  cx="50%"
                  cy="50%"
                  innerRadius={0}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {remoteData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[(index + 2) % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="w-2/5 flex flex-col gap-2 justify-center pl-4 border-l border-gray-800">
            {remoteData.map((item, index) => (
              <div key={index} className="flex items-center gap-2 text-xs">
                <span
                  className="w-3 h-3 rounded-full shrink-0"
                  style={{ backgroundColor: COLORS[(index + 2) % COLORS.length] }}
                ></span>
                <span className="text-gray-300 font-semibold truncate">{item.name}:</span>
                <span className="text-gray-400">{item.value} tin</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
