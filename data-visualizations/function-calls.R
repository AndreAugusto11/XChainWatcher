library(ggplot2)
library(tidyverse)
library(lubridate)

decoded_txs<-read_csv("../raw-data/ronin-bridge/decoded_data/decoded_txs_aggregated.csv")

# Preprocess the timestamp to remove 'GMT'
decoded_txs$timestamp <- gsub(" GMT", "", decoded_txs$timestamp)

# Convert timestamp column to POSIXct (date-time) format using lubridate with correct format
decoded_txs$timestamp <- parse_date_time(decoded_txs$timestamp, orders = "a, d b Y H:M:S")

invalid_timestamps <- decoded_txs[is.na(decoded_txs$timestamp), ]
print(invalid_timestamps)

###### batchSubmitWithdrawalSignatures ######

withdrawal_sigs <- decoded_txs[decoded_txs$function_name == "batchSubmitWithdrawalSignatures", ]

# Create a new column for the 24-hour interval
withdrawal_sigs$interval <- floor_date(withdrawal_sigs$timestamp, "6 hours")

# Group by the 24-hour interval and sum the counts
agg_withdrawal_sigs <- withdrawal_sigs %>%
  group_by(interval) %>%
  summarise(total_count = sum(count, na.rm = TRUE))

# Plot the aggregated data
ggplot(agg_withdrawal_sigs, aes(x = interval, y = total_count)) +
  geom_line() +
  labs(title = "Withdrawal Signatures per 6-hour Interval", x = "Interval", y = "Total Count") +
  
  theme(
    panel.background = element_rect(fill = "white", color = NA),
    panel.grid.major = element_line(color = "lightgray"),
    panel.grid.minor = element_blank(),
    axis.line = element_line(color = "black"),
    axis.text.x = element_text(angle = 90, hjust = 1)
  )

###### batchDepositERCTokenFor ######

batch_deposit <- decoded_txs[decoded_txs$function_name == "batchDepositERCTokenFor", ]

# Create a new column for the 24-hour interval
batch_deposit$interval <- floor_date(batch_deposit$timestamp, "6 hours")

# Group by the 24-hour interval and sum the counts
agg_batch_deposit <- batch_deposit %>%
  group_by(interval) %>%
  summarise(total_count = sum(count, na.rm = TRUE))

# Plot the aggregated data
ggplot(agg_batch_deposit, aes(x = interval, y = total_count)) +
  geom_line() +
  labs(title = "Withdrawal Signatures per 6-hour Interval", x = "Interval", y = "Total Count") +
  
  theme(
    panel.background = element_rect(fill = "white", color = NA),
    panel.grid.major = element_line(color = "lightgray"),
    panel.grid.minor = element_blank(),
    axis.line = element_line(color = "black"),
    axis.text.x = element_text(angle = 90, hjust = 1)
  )

###### MERGE DATA ######

# Assuming agg_withdrawal_sigs is one dataframe and agg_batch_deposit is another dataframe
min(agg_withdrawal_sigs$interval)

# Find the full range of intervals
full_range <- seq(min(agg_withdrawal_sigs$interval), max(agg_withdrawal_sigs$interval), by = "6 hours")

# Create a template dataframe with the full range of intervals and zeros for counts
template_df <- data.frame(interval = full_range, total_count = 0)

# Append missing intervals with zeros to agg_withdrawal_sigs
agg_withdrawal_sigs <- bind_rows(agg_withdrawal_sigs, template_df %>% anti_join(agg_withdrawal_sigs, by = "interval"))

# Append missing intervals with zeros to agg_batch_deposit
agg_batch_deposit <- bind_rows(agg_batch_deposit, template_df %>% anti_join(agg_batch_deposit, by = "interval"))

# Sort the datasets by interval
agg_withdrawal_sigs <- agg_withdrawal_sigs[order(agg_withdrawal_sigs$interval), ]
agg_batch_deposit <- agg_batch_deposit[order(agg_batch_deposit$interval), ]

ggplot() +
  geom_point(size=0.5, data = agg_withdrawal_sigs, aes(x = interval, y = total_count, color = "withdrawals")) +
  geom_line(data = agg_withdrawal_sigs, aes(x = interval, y = total_count, color = "withdrawals")) +
  geom_point(size=0.5, data = agg_batch_deposit, aes(x = interval, y = total_count, color = "deposits")) +
  geom_line(data = agg_batch_deposit, aes(x = interval, y = total_count, color = "deposits")) +
  labs(
    #title = "Function Calls to Withdraw/Deposit Funds into Ronin Bridge",
    x = "Date",
    y = "Function Calls"
  ) +
  scale_y_log10(limits = c(1, 10^4)) +
  geom_vline(xintercept = as.POSIXct("2022-03-23 13:31:00", tz = "GMT"), linetype = "dashed", color = "red", size = 0.5) +
  annotate("text", as.POSIXct("2022-03-20 16:31:00", tz = "GMT"), 10^4, hjust = .5, label = "Attack Transaction", colour = "red") +
  geom_vline(xintercept = as.POSIXct("2022-03-29 16:00:00", tz = "GMT"), linetype = "dashed", color = "black", size = 0.5) +
  annotate("text", as.POSIXct("2022-03-26 20:00:00", tz = "GMT"), 10^4, hjust = .5, label = "Attack Discovered", colour = "black") +
  theme(
    text = element_text(family = "serif"),
    plot.title = element_text(face = "bold", size = rel(1.5), hjust = 0.5),
    panel.background = element_rect(fill = "white", color = NA),
    panel.grid.major.y = element_line(color = 6,
                                      size = 0.1,
                                      linetype = 2),
    panel.grid.minor = element_blank(),
    axis.line = element_line(color = "black"),
    axis.title.y=element_text(size=14),
    axis.title.x=element_text(size=14, margin = margin(t = 5, r = 0, b = 0, l = 0)),
    axis.text = element_text(size = 10),
    axis.text.x = element_text(angle = 90, hjust = 0),
    legend.margin=margin(t = -0.2, unit='cm'),
    legend.position = c(0.1, 0.25),
    legend.background = element_rect(size=0.1)
  ) +
  scale_x_datetime(date_breaks = "24 hours", date_labels = "%Y-%m-%d") +
  scale_color_manual("", breaks = c("withdrawals", "deposits"), values = c("royalblue3", "magenta"))
