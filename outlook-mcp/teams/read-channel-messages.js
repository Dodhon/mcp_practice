/**
 * Read Channel Messages handler
 */
const { callGraphAPI } = require('../utils/graph-api');
const { ensureAuthenticated } = require('../auth');

async function handleReadChannelMessages(args) {
  try {
    const { teamId, channelId, count = 20 } = args;
    
    // Validate required parameters
    if (!teamId) {
      throw new Error('teamId is required');
    }
    if (!channelId) {
      throw new Error('channelId is required');
    }
    
    // Validate count parameter
    if (count > 50) {
      throw new Error('Count cannot exceed 50');
    }

    // Get access token
    const accessToken = await ensureAuthenticated();
    
    // Build query parameters
    const queryParams = {
      $orderby: 'createdDateTime desc',
      $top: count,
      $expand: 'replies'
    };
    
    // Get channel messages
    const response = await callGraphAPI(accessToken, 'GET', `teams/${teamId}/channels/${channelId}/messages`, null, queryParams);

    const messages = response.value.map(message => ({
      id: message.id,
      createdDateTime: message.createdDateTime,
      lastModifiedDateTime: message.lastModifiedDateTime,
      messageType: message.messageType,
      importance: message.importance,
      webUrl: message.webUrl,
      from: {
        user: {
          id: message.from?.user?.id,
          displayName: message.from?.user?.displayName,
          userIdentityType: message.from?.user?.userIdentityType
        }
      },
      body: {
        contentType: message.body?.contentType,
        content: message.body?.content
      },
      mentions: message.mentions || [],
      reactions: message.reactions || [],
      replyCount: message.replies?.length || 0,
      replies: message.replies?.map(reply => ({
        id: reply.id,
        createdDateTime: reply.createdDateTime,
        from: {
          user: {
            id: reply.from?.user?.id,
            displayName: reply.from?.user?.displayName
          }
        },
        body: {
          contentType: reply.body?.contentType,
          content: reply.body?.content
        }
      })) || []
    }));

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            success: true,
            teamId: teamId,
            channelId: channelId,
            count: messages.length,
            messages: messages
          }, null, 2)
        }
      ]
    };

  } catch (error) {
    console.error('Error reading channel messages:', error);
    
    if (error.message === 'Authentication required') {
      return {
        content: [{ 
          type: "text", 
          text: "Authentication required. Please use the 'authenticate' tool first."
        }]
      };
    }
    
    let errorMessage = 'Failed to read channel messages';
    if (error.message.includes('403')) {
      errorMessage = 'Insufficient permissions to read messages. Please ensure the application has ChannelMessage.Read.All permission.';
    } else if (error.message.includes('401')) {
      errorMessage = 'Authentication failed. Please ensure you are logged in.';
    } else if (error.message.includes('404')) {
      errorMessage = `Team or channel not found. Please verify the teamId '${args.teamId}' and channelId '${args.channelId}' are correct.`;
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

module.exports = handleReadChannelMessages; 