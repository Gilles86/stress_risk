function [block_level_k,CH_block_level_k] = pseudo_rand(SUBID,bot_levels,Mapping)

permutations = perms(bot_levels);
permutations = [permutations ; permutations(1,:); permutations(3,:); permutations(5,:)];

levels = circshift( permutations , Mapping(Mapping(:,2)==SUBID,1));
block_level_k = levels(1,:) ;

% randID = Mapping(Mapping(:,2)==SUBID,1);
% CH_block_level_k = circshift([2 3 2 3],rem(randID,2));

end