
%==========================================================================
% draw cue (self/other)
% isabella.wagner@univie.ac.at
%==========================================================================

clear image text

% if curr.cnd == 1        % self
    
%     if parm.exp.show_arrow == true
%         
%         image = parm.ptb.img.arrow_self.image;
%         
%     else
%         
%         image = parm.ptb.img.self.image;
%         
%     end

    text = reward_text('targetYou');
    
% elseif curr.cnd == 2    % other
    
%     if parm.exp.show_arrow == true
%         
%         image = parm.ptb.img.arrow_other.image;
%         
%     else
%         
%         image = parm.ptb.img.other.image;
%         
%     end
%     
%     text = reward_text('targetOther',parm.info.subj2ID);
%     
% end

clear texture; texture = Screen('MakeTexture', parm.ptb.scr.w, image);

Screen('DrawTextures',  parm.ptb.scr.w, texture, [], parm.ptb.img.cue);

% prepare cue text above

util_text(parm.ptb.scr.w,parm.ptb.scr.font,parm.ptb.scr.stimfont,parm.ptb.scr.fontcol,1)

DrawFormattedText( parm.ptb.scr.w, text, 'center', parm.ptb.img.pos_cue_text);
