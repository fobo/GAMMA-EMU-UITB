%% ============================================================
%  GAMMA Population Log - Visualization Script
%  Expects: *_poplog.csv produced by train.py
%% ============================================================

clear; clc; close all;

files = {
   % "mobilePOP5.csv"
   % "mobilePOP10.csv"
    "vgg16S2-6.csv"
    "shuffleS2-6.csv"
    "mnasnetS2-6.csv"
    "mobileS2-6.csv"
};

out_dir = fullfile(pwd, 'figures');
if ~exist(out_dir, 'dir')
    mkdir(out_dir);
end

n_files = numel(files);
min_runtime = nan(n_files, 1);

for fi = 1:n_files
    fprintf("Processing %s...\n", files{fi});


%% --- 1. Load the CSV ---
csv_file = files{fi};  % <-- change this
T = readtable(csv_file, ...
    'TextType', 'string', ...
    'VariableNamingRule', 'preserve', ...
    'HeaderLines', 0, ...
    'ReadVariableNames', true);
disp(T.Properties.VariableNames)


%% --- 2. Parse scalar columns ---
N = height(T);

is_valid    = strcmp(T.is_valid, 'True');
is_elite    = strcmp(T.is_elite, 'True');
% generation column may already be numeric from readtable
if isnumeric(T.generation)
    generation = T.generation;
else
    generation = str2double(T.generation);
end
if isnumeric(T.individual_idx)
    indv_idx = T.individual_idx;
else
    indv_idx = str2double(T.individual_idx);
end

if isnumeric(T.num_levels)
    num_levels = T.num_levels;
else
    num_levels = str2double(T.num_levels);
end
if isnumeric(T.runtime)
    runtime = T.runtime;
else
    runtime = str2double(T.runtime);
end
energy      = str2double(T.energy);
area        = str2double(T.area);
l1_size     = str2double(T.l1_size);
l2_size     = str2double(T.l2_size);
num_pe      = str2double(T.num_pe);
throughput  = str2double(T.throughput);
power       = str2double(T.power);

% --- reward parsing ---
reward_str = strrep(T.reward, '-Infinity', 'NaN');
reward_str = strrep(reward_str, 'Infinity', 'NaN');
reward = nan(N, 1);
for i = 1:N
    try
        vals = jsondecode(reward_str(i));
        reward(i) = vals(1);
    catch
        % leave as NaN
    end
end

% --- define all valid flags after reward is fully populated ---
valid      = is_valid;
has_obs    = is_valid & ~isnan(runtime) & ~isnan(energy) & ~isnan(area);
valid_mask = is_valid & ~isnan(reward);

fprintf('N: %d\n', N);
fprintf('is_valid true: %d\n', sum(is_valid));
fprintf('has_obs: %d\n', sum(has_obs));
fprintf('valid_mask: %d\n', sum(valid_mask));
fprintf('runtime non-NaN: %d\n', sum(~isnan(runtime)));
fprintf('reward non-NaN: %d\n', sum(~isnan(reward)));

%% --- 3. Parse genome_vec into a matrix ---
feature_names = jsondecode(T.feature_names(1));
n_features = numel(feature_names);

genome_mat = nan(N, n_features);
parse_failures = 0;
for i = 1:N
    try
        vec = jsondecode(T.genome_vec(i));
        if numel(vec) == n_features
            genome_mat(i, :) = vec';
        else
            parse_failures = parse_failures + 1;
        end
    catch
        parse_failures = parse_failures + 1;
    end
end
fprintf('Genome parse failures: %d / %d\n', parse_failures, N);
fprintf('Genome rows with any valid data: %d\n', sum(any(~isnan(genome_mat), 2)));

%% --- 4. Parse sp_dims ---
sp_dim_L1 = strings(N, 1);
sp_dim_L2 = strings(N, 1);
for i = 1:N
    try
        dims = jsondecode(T.sp_dims(i));
        sp_dim_L1(i) = dims(1);
        if numel(dims) >= 2
            sp_dim_L2(i) = dims(2);
        end
    catch
        % leave as empty string
    end
end

gen_ids = unique(generation);
n_gens  = numel(gen_ids);

% add this line for other attributes to make graphs easy
min_runtime(fi) = min(runtime, [], 'omitnan');


%% ============================================================
%  PLOT 1: Convergence Curve
%% ============================================================
fig1 = figure('Name', 'Convergence Curve');
best_per_gen = nan(n_gens, 1);
for gi = 1:n_gens
    mask = generation == gen_ids(gi) & valid_mask;
    if any(mask)
        best_per_gen(gi) = max(reward(mask));
    end
end
plot(gen_ids, abs(best_per_gen), 'b-o', 'LineWidth', 2, 'MarkerSize', 5);
xlabel('Generation'); ylabel('Best Reward (absolute value)');
[~, name, ~] = fileparts(files{fi});
title('Convergence: Best Fitness per Generation ' + name);
grid on;

saveas(fig1, fullfile(out_dir, sprintf('%s_convergence.png', name)));
%% ============================================================
%  PLOT: Chernoff Faces
%% ============================================================
face_feature_cols = [1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 13, 20, 21, 22, 23, 26, 27];

best_rows = nan(n_gens, 1);
for gi = 1:n_gens
    mask = find(generation == gen_ids(gi) & valid_mask);
    if isempty(mask)
        continue;
    end
    [~, best_local] = max(reward(mask));
    best_rows(gi) = mask(best_local);
end
best_rows = best_rows(~isnan(best_rows) & best_rows > 0);

if isempty(best_rows)
    fprintf('No valid best rows found for faces plot — skipping.\n');
else
    F = genome_mat(best_rows, face_feature_cols);
    F_norm = (F - min(F)) ./ (max(F) - min(F) + 1e-8);
    n_faces = min(20, size(F_norm, 1));
    step = max(1, floor(size(F_norm, 1) / n_faces));
    face_idx = 1:step:size(F_norm, 1);
    F_plot = F_norm(face_idx, :);
    face_gen_labels = arrayfun(@(g) sprintf('Gen %d', gen_ids(face_idx(g))), ...
        1:numel(face_idx), 'UniformOutput', false);

    f_std = std(F_plot);
    F_plot = F_plot(:, f_std > 1e-8);

    if size(F_plot, 2) < 1 || size(F_plot, 1) < 1
        fprintf('Face feature matrix empty after filtering — skipping.\n');
    else
        fig2 = figure('Name', 'Chernoff Faces — Best Mapping per Generation', ...
            'Position', [100, 100, 1400, 900]);
        glyphplot(F_plot, ...
            'Glyph',     'face', ...
            'ObsLabels', face_gen_labels, ...
            'Features',  1:size(F_plot, 2));
        title('Chernoff Faces: Best Hardware Mapping per Generation for ' + name);

        saveas(fig2, fullfile(out_dir, sprintf('%s_chernoff_faces.png', name)));
    end
end
end

%% ============================================================
%  PLOT: Latency Comparison
%% ============================================================
fig3 = figure;
bar(min_runtime);

x_names = {
    "VGG16"
    "ShuffleNetv2"
    "MnasNet"
    "MobileNetv2"
    %"80"
    %"160"
    }
n_names = numel(x_names);

set(gca, 'XTick', 1:n_names, 'XTickLabel', x_names);
xlabel('Model');
ylabel('Minimum Runtime (cycles)');
title('Minimum Latency Across Best Performing Models for sLevel Range 2 - 6');
grid on;
saveas(fig3, fullfile(out_dir, 'best_latency_comparison.png'));