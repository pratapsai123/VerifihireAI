import React from 'react';

export const MalpracticePanel = ({ 
  violations, 
  visible, 
  onClose, 
  onViewScreenshot 
}) => {
  // Aggregate counts of each violation type
  const counts = violations.reduce((acc, v) => {
    acc[v.violation_type] = (acc[v.violation_type] || 0) + 1;
    return acc;
  }, {});

  const getSeverityColor = (severity) => {
    switch (severity.toUpperCase()) {
      case 'HIGH':
        return '#ef4444'; // Red
      case 'MEDIUM':
        return '#f97316'; // Orange
      case 'LOW':
        return '#eab308'; // Yellow
      default:
        return '#94a3b8'; // Slate
    }
  };

  const formatViolationType = (type) => {
    switch (type) {
      case 'NO_FACE':
        return 'No Face Detected';
      case 'EXTRA_PERSON_DETECTED':
        return 'Extra Person Detected';
      case 'MOBILE_PHONE_DETECTED':
        return 'Mobile Phone Detected';
      case 'SCREEN_SHARE_STOPPED':
        return 'Screen Share Stopped';
      case 'MULTIPLE_FACES':
        return 'Multiple Faces Detected';
      case 'TAB_SWITCH':
        return 'Tab Switch Detected';
      case 'FULLSCREEN_EXIT':
        return 'Fullscreen Exit Detected';
      default:
        return type;
    }
  };

  const getViolationIcon = (type) => {
    switch (type) {
      case 'NO_FACE':
        return 'fa-user-slash';
      case 'EXTRA_PERSON_DETECTED':
        return 'fa-user-friends';
      case 'MOBILE_PHONE_DETECTED':
        return 'fa-mobile-alt';
      case 'SCREEN_SHARE_STOPPED':
        return 'fa-desktop';
      case 'MULTIPLE_FACES':
        return 'fa-users';
      case 'TAB_SWITCH':
        return 'fa-window-restore';
      case 'FULLSCREEN_EXIT':
        return 'fa-compress-arrows-alt';
      default:
        return 'fa-exclamation-triangle';
    }
  };

  return (
    <div className={`malpractice-sidebar ${!visible ? 'closed' : ''}`}>
      <div className="malpractice-header">
        <div className="malpractice-header-title">
          <i className="fas fa-shield-alt shield-icon"></i>
          <h3>Malpractice Log</h3>
        </div>
        <button className="close-malpractice" onClick={onClose}>
          <i className="fas fa-times"></i>
        </button>
      </div>

      {/* Violation Stats Cards */}
      <div className="malpractice-stats-grid">
        <div className="stat-card high-risk">
          <span className="stat-val">{counts['NO_FACE'] || 0}</span>
          <span className="stat-lbl">No Face</span>
        </div>
        <div className="stat-card high-risk">
          <span className="stat-val">{(counts['MULTIPLE_FACES'] || 0) + (counts['EXTRA_PERSON_DETECTED'] || 0)}</span>
          <span className="stat-lbl">Multi Face</span>
        </div>
        <div className="stat-card high-risk">
          <span className="stat-val">{counts['MOBILE_PHONE_DETECTED'] || 0}</span>
          <span className="stat-lbl">Mobile Phone</span>
        </div>
        <div className="stat-card high-risk">
          <span className="stat-val">{counts['SCREEN_SHARE_STOPPED'] || 0}</span>
          <span className="stat-lbl">No Screen</span>
        </div>
        <div className="stat-card med-risk">
          <span className="stat-val">{counts['TAB_SWITCH'] || 0}</span>
          <span className="stat-lbl">Tab Switch</span>
        </div>
        <div className="stat-card med-risk">
          <span className="stat-val">{counts['FULLSCREEN_EXIT'] || 0}</span>
          <span className="stat-lbl">Fullscreen Exits</span>
        </div>
      </div>

      {/* Violations Chronological Feed */}
      <div className="malpractice-feed">
        {violations.length === 0 ? (
          <div className="malpractice-empty">
            <i className="fas fa-check-circle success-badge-icon"></i>
            <p>No proctoring violations recorded. Candidate is normal.</p>
          </div>
        ) : (
          violations.map((violation, index) => {
            const date = new Date(violation.timestamp);
            const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            
            // Details description
            let detailMsg = '';
            if (violation.details) {
              const details = typeof violation.details === 'string' 
                ? JSON.parse(violation.details) 
                : violation.details;
              detailMsg = details.message || '';
            }

            return (
              <div key={violation.id || index} className="malpractice-card">
                <div className="malpractice-card-top">
                  <div className="malpractice-card-badge">
                    <span 
                      className="severity-dot" 
                      style={{ backgroundColor: getSeverityColor(violation.severity) }}
                    />
                    <i className={`fas ${getViolationIcon(violation.violation_type)} card-icon`}></i>
                    <strong className="violation-name">
                      {formatViolationType(violation.violation_type)}
                    </strong>
                  </div>
                  <span className="violation-time">{timeStr}</span>
                </div>

                <div className="malpractice-card-body">
                  <p className="violation-details-text">{detailMsg}</p>
                  
                  {violation.duration > 0 && (
                    <div className="violation-meta-item">
                      <i className="fas fa-hourglass-half"></i>
                      <span>Away Duration: {violation.duration}s</span>
                    </div>
                  )}

                  {/* Screenshot Thumbnail */}
                  {violation.screenshot_path && (
                    <div className="violation-screenshot-preview">
                      <img 
                        src={violation.screenshot_path} 
                        alt="Violation snapshot" 
                        onClick={() => onViewScreenshot(violation.screenshot_path)}
                      />
                      <div className="screenshot-overlay-hint" onClick={() => onViewScreenshot(violation.screenshot_path)}>
                        <i className="fas fa-search-plus"></i> View Snapshot
                      </div>
                    </div>
                  )}
                  {/* Fallback support for ws relative url mapping */}
                  {!violation.screenshot_path && violation.screenshot_url && (
                    <div className="violation-screenshot-preview">
                      <img 
                        src={violation.screenshot_url} 
                        alt="Violation snapshot" 
                        onClick={() => onViewScreenshot(violation.screenshot_url)}
                      />
                      <div className="screenshot-overlay-hint" onClick={() => onViewScreenshot(violation.screenshot_url)}>
                        <i className="fas fa-search-plus"></i> View Snapshot
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default MalpracticePanel;
