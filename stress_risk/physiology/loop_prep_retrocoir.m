% loop for running

sub_list = ['03'; '04'; '05'; '06'; '07';'08'; '09'; '10'; '11'; '12'; '13'; '14'; '15'; '16'; '17'];
sub_list = ['03'; '04']
errorL = [];
for sub = 1:length(sub_list)
    try 
       prepare_retroicor(sub_list(sub,:),'1');
    catch
        errorL = [errorL; sub_list(sub,:)];
    end
end




