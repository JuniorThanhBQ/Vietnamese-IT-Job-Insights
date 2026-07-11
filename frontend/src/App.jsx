import { useState, useEffect, useCallback } from 'react';
import {
  Briefcase,
  BarChart2,
  MessageSquare,
  Search,
  MapPin,
  DollarSign,
  Globe,
  Calendar,
  X,
  ExternalLink,
} from 'lucide-react';
import { useFetch } from './hooks/useFetch';
import { useChat } from './hooks/useChat';
import { JobCard } from './components/JobCard';
import { Analytics } from './components/Analytics';
import { ChatPanel } from './components/ChatPanel';

export default function App() {
  const [activeTab, setActiveTab] = useState('jobs');
  const [selectedJob, setSelectedJob] = useState(null);

  // Search filter states
  const [query, setQuery] = useState('');
  const [site, setSite] = useState('');
  const [seniority, setSeniority] = useState('');
  const [remotePolicy, setRemotePolicy] = useState('');
  const [page, setPage] = useState(1);
  const itemsPerPage = 8;

  // Custom fetch hooks
  const { data: jobsList, loading: jobsLoading, request: fetchJobs } = useFetch();
  const { data: analyticsData, loading: analyticsLoading, request: fetchAnalytics } = useFetch();

  // Custom chat hook
  const { messages, streaming, error: chatError, sendMessage, clearChat } = useChat();

  // Load jobs based on filters or query
  const loadJobs = useCallback(() => {
    const offset = (page - 1) * itemsPerPage;
    if (query.trim()) {
      // Use semantic search endpoint
      fetchJobs(`/api/v1/jobs/search?q=${encodeURIComponent(query)}&limit=20`);
    } else {
      // Use traditional filter list endpoint
      let url = `/api/v1/jobs?limit=${itemsPerPage}&offset=${offset}`;
      if (site) url += `&site=${site}`;
      if (seniority) url += `&seniority=${seniority}`;
      if (remotePolicy) url += `&remote_policy=${remotePolicy}`;
      fetchJobs(url);
    }
  }, [page, query, site, seniority, remotePolicy, fetchJobs]);

  // Reload jobs when filters or page changes
  useEffect(() => {
    loadJobs();
  }, [loadJobs]);

  // Load analytics when switching to analytics tab
  useEffect(() => {
    if (activeTab === 'analytics') {
      fetchAnalytics('/api/v1/jobs/analytics');
    }
  }, [activeTab, fetchAnalytics]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    loadJobs();
  };

  const handleResetFilters = () => {
    setQuery('');
    setSite('');
    setSeniority('');
    setRemotePolicy('');
    setPage(1);
    // Explicitly reload all jobs
    fetchJobs(`/api/v1/jobs?limit=${itemsPerPage}&offset=0`);
  };

  return (
    <div className="flex min-h-screen bg-[#080b11] text-gray-100 font-sans">
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-[#0c0f17] border-r border-gray-800 p-6 flex flex-col justify-between shrink-0">
        <div>
          {/* Logo */}
          <div className="flex items-center gap-3 mb-10">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-400 to-indigo-500 flex items-center justify-center text-white font-black text-lg shadow-lg shadow-blue-500/20">
              G
            </div>
            <div>
              <h1 className="text-sm font-black tracking-wider uppercase bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent m-0 leading-none">
                JD Insights
              </h1>
              <span className="text-[10px] text-gray-500 font-bold">VIETNAMESE IT JOBS</span>
            </div>
          </div>

          {/* Nav Links */}
          <nav className="space-y-1">
            <button
              onClick={() => setActiveTab('jobs')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all cursor-pointer ${
                activeTab === 'jobs'
                  ? 'bg-blue-600/10 border border-blue-500/30 text-blue-400'
                  : 'text-gray-400 hover:bg-gray-800/40 hover:text-gray-200 border border-transparent'
              }`}
            >
              <Briefcase size={18} />
              <span>Việc Làm IT</span>
            </button>

            <button
              onClick={() => setActiveTab('analytics')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all cursor-pointer ${
                activeTab === 'analytics'
                  ? 'bg-blue-600/10 border border-blue-500/30 text-blue-400'
                  : 'text-gray-400 hover:bg-gray-800/40 hover:text-gray-200 border border-transparent'
              }`}
            >
              <BarChart2 size={18} />
              <span>Xu Hướng Thị Trường</span>
            </button>

            <button
              onClick={() => setActiveTab('chat')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all cursor-pointer ${
                activeTab === 'chat'
                  ? 'bg-blue-600/10 border border-blue-500/30 text-blue-400'
                  : 'text-gray-400 hover:bg-gray-800/40 hover:text-gray-200 border border-transparent'
              }`}
            >
              <MessageSquare size={18} />
              <span>Trợ Lý AI Chat</span>
            </button>
          </nav>
        </div>

        {/* Sidebar Footer */}
        <div className="pt-6 border-t border-gray-800/60 text-center">
          <p className="text-[10px] text-gray-600 font-medium">Antigravity AI Client © 2026</p>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 p-8 overflow-y-auto h-screen">
        {/* Tab 1: Job listings dashboard */}
        {activeTab === 'jobs' && (
          <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-100">Khám Phá Việc Làm IT</h2>
                <p className="text-sm text-gray-400">
                  Tổng hợp bài tuyển dụng từ ITviec & TopDev hàng ngày
                </p>
              </div>
            </div>

            {/* Search & Filters */}
            <form onSubmit={handleSearchSubmit} className="glass-panel p-5 rounded-xl space-y-4">
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Search size={18} className="absolute left-3 top-3 text-gray-500" />
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Tìm kiếm thông minh (Ví dụ: Python Remote Hồ Chí Minh hoặc Node.js Junior)..."
                    className="w-full bg-gray-900/40 border border-gray-800 focus:border-blue-500/40 rounded-lg pl-10 pr-4 py-2.5 text-sm text-gray-100 placeholder-gray-500 focus:outline-none"
                  />
                </div>
                <button
                  type="submit"
                  className="px-5 py-2.5 rounded-lg text-sm font-bold bg-blue-600 hover:bg-blue-500 text-white transition-colors cursor-pointer"
                >
                  Tìm kiếm
                </button>
              </div>

              <div className="flex flex-wrap gap-4 items-center justify-between pt-2 border-t border-gray-800/40">
                <div className="flex flex-wrap gap-3">
                  {/* Site Filter */}
                  <select
                    value={site}
                    onChange={(e) => {
                      setSite(e.target.value);
                      setPage(1);
                    }}
                    className="bg-[#0f131c] border border-gray-800 rounded-lg px-3 py-1.5 text-xs text-gray-300 focus:outline-none"
                  >
                    <option value="">Nguồn tuyển dụng</option>
                    <option value="itviec">ITviec</option>
                    <option value="topdev">TopDev</option>
                  </select>

                  {/* Seniority Filter */}
                  <select
                    value={seniority}
                    onChange={(e) => {
                      setSeniority(e.target.value);
                      setPage(1);
                    }}
                    className="bg-[#0f131c] border border-gray-800 rounded-lg px-3 py-1.5 text-xs text-gray-300 focus:outline-none"
                  >
                    <option value="">Cấp bậc</option>
                    <option value="Intern">Intern</option>
                    <option value="Fresher">Fresher</option>
                    <option value="Junior">Junior</option>
                    <option value="Middle">Middle</option>
                    <option value="Senior">Senior</option>
                    <option value="Lead">Lead</option>
                    <option value="Manager">Manager</option>
                  </select>

                  {/* Remote Policy Filter */}
                  <select
                    value={remotePolicy}
                    onChange={(e) => {
                      setRemotePolicy(e.target.value);
                      setPage(1);
                    }}
                    className="bg-[#0f131c] border border-gray-800 rounded-lg px-3 py-1.5 text-xs text-gray-300 focus:outline-none"
                  >
                    <option value="">Hình thức làm việc</option>
                    <option value="Remote">Remote</option>
                    <option value="Hybrid">Hybrid</option>
                    <option value="Onsite">Onsite</option>
                  </select>
                </div>

                <button
                  type="button"
                  onClick={handleResetFilters}
                  className="text-xs text-gray-500 hover:text-gray-300 font-semibold cursor-pointer underline underline-offset-4"
                >
                  Xóa bộ lọc
                </button>
              </div>
            </form>

            {/* Jobs Grid */}
            {jobsLoading ? (
              <div className="flex flex-col items-center justify-center h-80 gap-3">
                <div className="w-10 h-10 rounded-full border-4 border-t-blue-500 border-gray-800 animate-spin"></div>
                <p className="text-gray-500 text-xs font-medium">Đang tìm các công việc IT...</p>
              </div>
            ) : !jobsList || (Array.isArray(jobsList) && jobsList.length === 0) ? (
              <div className="text-center py-16 glass-panel rounded-xl">
                <p className="text-gray-400 text-sm">Không tìm thấy công việc phù hợp.</p>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
                  {/* Semantic Search returns array of { job, similarity_score } */}
                  {query.trim()
                    ? jobsList.map((item, idx) => (
                        <JobCard
                          key={idx}
                          job={item.job || item}
                          onSelect={(j) => setSelectedJob(j)}
                        />
                      ))
                    : jobsList.map((job, idx) => (
                        <JobCard key={idx} job={job} onSelect={(j) => setSelectedJob(j)} />
                      ))}
                </div>

                {/* Pagination (Hide on semantic search because limit is fixed at 20) */}
                {!query.trim() && (
                  <div className="flex items-center justify-center gap-3 pt-6">
                    <button
                      disabled={page === 1}
                      onClick={() => setPage((p) => Math.max(1, p - 1))}
                      className="px-4 py-2 rounded-lg bg-gray-900 border border-gray-800 hover:border-gray-700 text-xs font-bold text-gray-300 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer transition-colors"
                    >
                      Trang trước
                    </button>
                    <span className="text-xs text-gray-400 font-semibold">Trang {page}</span>
                    <button
                      disabled={jobsList.length < itemsPerPage}
                      onClick={() => setPage((p) => p + 1)}
                      className="px-4 py-2 rounded-lg bg-gray-900 border border-gray-800 hover:border-gray-700 text-xs font-bold text-gray-300 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer transition-colors"
                    >
                      Trang sau
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Trend Analytics Dashboard */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-100">Xu Hướng Tuyển Dụng IT</h2>
              <p className="text-sm text-gray-400">
                Thống kê trực quan về tiền lương, vị trí địa lý, kỹ năng và chính sách làm việc
              </p>
            </div>
            <Analytics data={analyticsData} loading={analyticsLoading} />
          </div>
        )}

        {/* Tab 3: RAG AI Assistant chat */}
        {activeTab === 'chat' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-100">Virtual Assistant (RAG)</h2>
              <p className="text-sm text-gray-400">
                Hỏi đáp bằng ngôn ngữ tự nhiên được bổ trợ ngữ cảnh từ kho bài tuyển dụng hiện có
              </p>
            </div>
            <ChatPanel
              messages={messages}
              streaming={streaming}
              error={chatError}
              sendMessage={sendMessage}
              onClear={clearChat}
            />
          </div>
        )}
      </main>

      {/* Dialog Modal Overlay for Job Details */}
      {selectedJob && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-[#0b0e14] border border-gray-800 w-full max-w-3xl rounded-xl shadow-2xl flex flex-col max-h-[85vh] animate-in fade-in zoom-in-95 duration-200">
            {/* Modal Header */}
            <div className="p-5 border-b border-gray-800 flex items-start justify-between">
              <div>
                <span className="text-[10px] font-extrabold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 uppercase">
                  {selectedJob.source_site}
                </span>
                <h3 className="text-xl font-bold text-gray-100 mt-2">{selectedJob.title}</h3>
                <p className="text-sm text-gray-400 font-semibold mt-1">
                  {selectedJob.company?.name}
                </p>
              </div>
              <button
                onClick={() => setSelectedJob(null)}
                className="p-1 rounded-lg hover:bg-gray-800 text-gray-500 hover:text-gray-300 transition-colors cursor-pointer"
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Body */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Metadata Badges */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gray-900/50 border border-gray-800/80 p-3 rounded-lg flex items-center gap-3">
                  <MapPin className="text-gray-500 shrink-0" size={20} />
                  <div>
                    <span className="text-[10px] text-gray-500 font-bold block uppercase">
                      Địa điểm
                    </span>
                    <span className="text-xs text-gray-300 font-semibold truncate block">
                      {selectedJob.company?.address || 'Việt Nam'}
                    </span>
                  </div>
                </div>

                <div className="bg-gray-900/50 border border-gray-800/80 p-3 rounded-lg flex items-center gap-3">
                  <DollarSign className="text-gray-500 shrink-0" size={20} />
                  <div>
                    <span className="text-[10px] text-gray-500 font-bold block uppercase">
                      Mức lương
                    </span>
                    <span className="text-xs text-emerald-400 font-semibold block">
                      {selectedJob.salary_min && selectedJob.salary_max
                        ? `${(selectedJob.salary_min / 1000000).toFixed(0)}M - ${(
                            selectedJob.salary_max / 1000000
                          ).toFixed(0)}M ${selectedJob.salary_currency}`
                        : selectedJob.salary_raw || 'Thương lượng'}
                    </span>
                  </div>
                </div>

                <div className="bg-gray-900/50 border border-gray-800/80 p-3 rounded-lg flex items-center gap-3">
                  <Globe className="text-gray-500 shrink-0" size={20} />
                  <div>
                    <span className="text-[10px] text-gray-500 font-bold block uppercase">
                      Làm việc
                    </span>
                    <span className="text-xs text-gray-300 font-semibold block">
                      {selectedJob.remote_policy}
                    </span>
                  </div>
                </div>

                <div className="bg-gray-900/50 border border-gray-800/80 p-3 rounded-lg flex items-center gap-3">
                  <Calendar className="text-gray-500 shrink-0" size={20} />
                  <div>
                    <span className="text-[10px] text-gray-500 font-bold block uppercase">
                      Ngày đăng
                    </span>
                    <span className="text-xs text-gray-300 font-semibold block">
                      {selectedJob.posting_time
                        ? new Date(selectedJob.posting_time).toLocaleDateString('vi-VN')
                        : 'Hôm nay'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Description */}
              <div className="space-y-2">
                <h4 className="text-sm font-bold text-gray-300 uppercase tracking-wider">
                  Mô tả công việc
                </h4>
                <div className="text-gray-400 text-sm leading-relaxed whitespace-pre-wrap pl-3 border-l-2 border-blue-500/40">
                  {selectedJob.description}
                </div>
              </div>

              {/* Requirements */}
              {selectedJob.requirements && (
                <div className="space-y-2">
                  <h4 className="text-sm font-bold text-gray-300 uppercase tracking-wider">
                    Yêu cầu ứng viên
                  </h4>
                  <div className="text-gray-400 text-sm leading-relaxed whitespace-pre-wrap pl-3 border-l-2 border-indigo-500/40">
                    {selectedJob.requirements}
                  </div>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-gray-800 flex justify-end gap-2 bg-[#080a0f]">
              <button
                onClick={() => setSelectedJob(null)}
                className="px-4 py-2 rounded-lg text-xs font-bold bg-gray-850 hover:bg-gray-800 text-gray-400 hover:text-gray-200 transition-colors cursor-pointer"
              >
                Đóng
              </button>
              <a
                href={selectedJob.url}
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 rounded-lg text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white transition-colors flex items-center gap-1.5 cursor-pointer"
              >
                Ứng tuyển ngay
                <ExternalLink size={14} />
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
