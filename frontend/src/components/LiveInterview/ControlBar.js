import React from 'react';

export const ControlBar = ({
  isMuted,
  isCameraOn,
  isScreenSharing,
  chatPanelVisible,
  chatUnreadCount,
  MY_ROLE,
  screenShareLocked,
  screenShareHolder,
  toggleMic,
  toggleCamera,
  toggleScreenShare,
  setChatPanelVisible,
  handleEndInterview
}) => {
  return (
    <div className="control-bar-wrapper">
      <div className="control-bar">
        <button
          className={`control-btn ${!isMuted ? 'active' : 'off'}`}
          onClick={toggleMic}
          title={isMuted ? "Unmute" : "Mute"}
        >
          <div className="icon-circle">
            <i className={`fas fa-microphone${isMuted ? '-slash' : ''}`}></i>
          </div>
          <span className="control-label">{isMuted ? "Unmute" : "Mute"}</span>
        </button>

        <button
          className={`control-btn ${isCameraOn ? 'active' : 'off'}`}
          onClick={toggleCamera}
          title={isCameraOn ? "Stop Video" : "Start Video"}
        >
          <div className="icon-circle">
            <i className={`fas fa-video${!isCameraOn ? '-slash' : ''}`}></i>
          </div>
          <span className="control-label">{isCameraOn ? "Stop Video" : "Start Video"}</span>
        </button>

        <button
          className={`control-btn screen-share ${isScreenSharing ? 'active' : ''}`}
          onClick={toggleScreenShare}
          title="Share Screen"
          disabled={screenShareLocked && screenShareHolder !== MY_ROLE}
        >
          <div className="icon-circle">
            <i className="fas fa-desktop"></i>
          </div>
          <span className="control-label">Share</span>
        </button>

        <button
          className={`control-btn ${chatPanelVisible ? 'active' : ''}`}
          onClick={() => setChatPanelVisible(!chatPanelVisible)}
          title="Chat"
        >
          <div className="icon-circle" style={{ position: 'relative' }}>
            <i className="fas fa-comment-alt"></i>
            {!chatPanelVisible && chatUnreadCount > 0 && (
              <span className="badge">{chatUnreadCount}</span>
            )}
          </div>
          <span className="control-label">Chat</span>
        </button>

        <button 
          className="control-btn end-call end-call-danger" 
          onClick={() => handleEndInterview(true)}
          title="End Interview"
        >
          <div className="icon-circle">
            <i className="fas fa-phone-slash"></i>
          </div>
          <span className="control-label">End</span>
        </button>
      </div>
    </div>
  );
};

export default ControlBar;
