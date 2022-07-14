function Quest_answers = questionaire(data)
%%

% VAS questions
drawText(data.w, 'Please answer a few quick questions!', data.PTB.colors.textcolor, data.PTB.fontsizes.text);
Screen(data.w, 'Flip');
WaitSecs(2/data.speedup_factor);

Qestions(1,1) = {'I feel joy.'};
Qestions(2,1) = {'I feel anger.'};
Qestions(3,1) = {'I feel stressed.'};
Qestions(4,1) = {'I feel disgusted.'};
Qestions(5,1) = {'I feel fear.'};
Qestions(6,1) = {'I feel surprised.'};
Qestions(7,1) = {'I feel sad.'};

for ii = 1:numel(Qestions)
    
    Quest_answers(ii,1) = get_likert_rating(data.w, data.wx, data.hx_full, data, Qestions{ii,1});
    
end

Screen(data.w,'Flip');

end

