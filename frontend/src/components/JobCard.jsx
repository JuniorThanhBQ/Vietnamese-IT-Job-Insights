import { MapPin, DollarSign, Briefcase, Globe, ExternalLink } from 'lucide-react';

export function JobCard({ job, onSelect }) {
  const formatSalary = () => {
    if (job.salary_min && job.salary_max) {
      const minM = (job.salary_min / 1000000).toFixed(0);
      const maxM = (job.salary_max / 1000000).toFixed(0);
      return `${minM}M - ${maxM}M ${job.salary_currency}`;
    }
    return job.salary_raw || 'Thương lượng';
  };

  return (
    <div className="glass-card p-5 rounded-xl flex flex-col justify-between h-full hover:shadow-2xl">
      <div>
        <div className="flex items-start justify-between gap-3 mb-3">
          <div>
            <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
              {job.source_site === 'itviec' ? 'ITviec' : 'TopDev'}
            </span>
            <h3 className="text-lg font-bold text-gray-100 mt-2 line-clamp-2 leading-tight">
              {job.title}
            </h3>
          </div>
          {job.company?.logo_url && (
            <img
              src={job.company.logo_url}
              alt={job.company.name}
              className="w-12 h-12 rounded-lg object-contain bg-white p-1 border border-gray-800"
            />
          )}
        </div>

        <p className="text-sm font-semibold text-gray-300 mb-4">{job.company?.name}</p>

        <div className="space-y-2.5 text-sm text-gray-400">
          <div className="flex items-center gap-2">
            <MapPin size={16} className="text-gray-500 shrink-0" />
            <span className="truncate">{job.company?.address || 'Việt Nam'}</span>
          </div>

          <div className="flex items-center gap-2">
            <DollarSign size={16} className="text-gray-500 shrink-0" />
            <span className="text-emerald-400 font-semibold">{formatSalary()}</span>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5">
              <Briefcase size={16} className="text-gray-500 shrink-0" />
              <span>{job.seniority}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Globe size={16} className="text-gray-500 shrink-0" />
              <span>{job.remote_policy}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-5 flex gap-2">
        <button
          onClick={() => onSelect(job)}
          className="flex-1 text-center py-2 rounded-lg text-sm font-bold bg-blue-600 hover:bg-blue-500 text-white transition-colors cursor-pointer"
        >
          Xem chi tiết
        </button>
        <a
          href={job.url}
          target="_blank"
          rel="noopener noreferrer"
          className="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors border border-gray-700 flex items-center justify-center"
          title="Xem tin gốc"
        >
          <ExternalLink size={16} />
        </a>
      </div>
    </div>
  );
}
