/**
 * Send Channel Message handler
 */
const { callGraphAPI } = require('../utils/graph-api');
const { ensureAuthenticated } = require('../auth');

async function handleSendChannelMessage(args) {
  try {
    const { teamId, channelId, message, contentType = 'text' } = args;
    
    // Validate required parameters
    if (!teamId) {
      throw new Error('teamId is required');
    }
    if (!channelId) {
      throw new Error('channelId is required');
    }
    if (!message || message.trim().length === 0) {
      throw new Error('message is required and cannot be empty');
    }

    // Get access token
    const accessToken = await ensureAuthenticated();
    
    // Prepare message body
    const messageBody = {
      body: {
        contentType: contentType,
        content: message.trim()
      }
    };

    // Send message to channel
    const response = await callGraphAPI(accessToken, 'POST', `teams/${teamId}/channels/${channelId}/messages`, messageBody);

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            success: true,
            messageId: response.id,
            teamId: teamId,
            channelId: channelId,
            sentAt: response.createdDateTime,
            webUrl: response.webUrl,
            message: {
              content: response.body.content,
              contentType: response.body.contentType
            }
          }, null, 2)
        }
      ]
    };

  } catch (error) {
    console.error('Error sending channel message:', error);
    
    if (error.message === 'Authentication required') {
      return {
        content: [{ 
          type: "text", 
          text: "Authentication required. Please use the 'authenticate' tool first."
        }]
      };
    }
    
    let errorMessage = 'Failed to send message to channel';
    if (error.message.includes('403')) {
      errorMessage = 'Insufficient permissions to send messages. Please ensure the application has ChannelMessage.Send permission.';
    } else if (error.message.includes('401')) {
      errorMessage = 'Authentication failed. Please ensure you are logged in.';
    } else if (error.message.includes('404')) {
      errorMessage = `Team or channel not found. Please verify the teamId '${args.teamId}' and channelId '${args.channelId}' are correct.`;
    } else if (error.message.includes('400')) {
      errorMessage = 'Invalid message content or format. Please check your message and content type.';
    } else if (error.message) {
      errorMessage = error.message;
    }

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            success: false,
            error: errorMessage,
            teamId: args.teamId,
            channelId: args.channelId
          }, null, 2)
        }
      ]
    };
  }
}

module.exports = handleSendChannelMessage; 